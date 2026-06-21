"""
extract_shorthand.py
====================
Extract shorthand forms from a PDF such as "5,000 Most-Used Shorthand Forms"
and save each one as a PNG named after its English word.

Pipeline (per page):
  1. Render the PDF page to a high-DPI image.
  2. Run Tesseract OCR to find every printed word + its bounding box.
  3. Filter to "real" entry words (lowercase, on a column's left margin,
     not a section header, not a sub-label like "2-s" or "1 cause").
  4. For each remaining word, treat its bounding box as the row anchor:
     - vertical band = top..bottom of the word, padded
     - horizontal slice = just past the word's right edge, to the column's
       right gutter
     - inside that slice, do connected-component analysis and pick the
       rightmost ink cluster — that's the shorthand.
  5. Save the cropped shorthand to outdir as <word>.png. If the word has
     already been seen, suffix with _2, _3, ...

Usage:
    python extract_shorthand.py input.pdf outdir/ [--dpi 300] [--start 1] [--end 71]

Requires:
    pip install pymupdf pytesseract pillow opencv-python numpy
    + Tesseract binary (Windows: https://github.com/UB-Mannheim/tesseract/wiki)
      Tell the script where it lives if it's not on PATH:
        --tesseract-cmd "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
"""

import argparse
import logging
import re
import sys
from collections import Counter
from pathlib import Path

import cv2
import fitz  # PyMuPDF
import numpy as np
import pytesseract
from PIL import Image

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log = logging.getLogger("shorthand")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
WORD_RE = re.compile(r"^[a-z]{3,}(?:'[a-z]+)?$")  # plain lowercase entry words, ≥3 chars

# Words that look like entries but are actually section / structural text.
# Most of these are filtered by other rules (uppercase, position) but listing
# explicit ones is a useful safety net.
STOPWORDS = {
    "the", "of", "is", "in", "and", "to", "for", "by", "as", "or",
    "are", "be", "etc", "joining", "expressed", "blend", "common",
    "words", "forms", "most", "used", "shorthand", "sound", "sign",
    "two", "signs", "heard", "brief", "suffix", "following",
}


def render_page(pdf_path: Path, page_num: int, dpi: int) -> np.ndarray:
    """Render a single PDF page (0-indexed) to a grayscale numpy array."""
    with fitz.open(pdf_path) as doc:
        page = doc[page_num]
        pix = page.get_pixmap(dpi=dpi)
        rgb = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return np.array(rgb.convert("L"))


def detect_columns(page: np.ndarray, num_columns: int = 3) -> list[tuple[int, int]]:
    """
    Detect column boundaries by finding wide vertical whitespace gutters.

    Uses ink projection from the body of the page only — header and footer
    rows (which often span the full width and would fill the column gutters)
    are excluded by analyzing the ink-density profile per row first.

    Returns a list of (x_left, x_right) for each column, ordered left-to-right.
    """
    h, w = page.shape
    ink = (page < 150).astype(np.uint8)

    # Identify body rows by looking at row ink density. Rows with very low or
    # very high ink (whitespace and headers) are excluded. Pure body rows
    # have moderate ink that's concentrated in the columns.
    row_ink = ink.sum(axis=1)
    median_row_ink = np.median(row_ink[row_ink > 0]) if (row_ink > 0).any() else 0
    # Headers tend to have ink spread across the full width => high ink count
    # Body rows have ink only in narrow column bands => moderate ink count
    # Pick rows with row_ink between 0.1x and 1.5x the median
    body_mask = (row_ink > median_row_ink * 0.1) & (row_ink < median_row_ink * 2.5)
    body_rows = np.where(body_mask)[0]

    if len(body_rows) < h * 0.3:
        # Fallback: use full page
        body_ink = ink
    else:
        body_ink = ink[body_rows, :]

    col_ink = body_ink.sum(axis=0)

    threshold = max(2, col_ink.max() * 0.02)
    is_gutter = col_ink < threshold

    # Minimum gutter width scales with page width (~1.5% of width).
    min_gutter_w = max(10, int(w * 0.015))

    gutters = []
    in_gutter = False
    start = 0
    for x in range(w):
        if is_gutter[x] and not in_gutter:
            start = x
            in_gutter = True
        elif not is_gutter[x] and in_gutter:
            if x - start >= min_gutter_w:
                gutters.append((start, x))
            in_gutter = False
    if in_gutter and w - start >= min_gutter_w:
        gutters.append((start, w))

    if len(gutters) < num_columns + 1:
        # Fallback: split the page evenly
        log.warning(
            "Only found %d gutters; falling back to even split", len(gutters)
        )
        col_w = w // num_columns
        return [(i * col_w, (i + 1) * col_w) for i in range(num_columns)]

    # First gutter = left page margin, last = right margin.
    # Inner gutters separate columns. We want exactly (num_columns + 1) edges.
    # Sort gutters by their CENTER x to keep it deterministic.
    gutters.sort(key=lambda g: (g[0] + g[1]) / 2)

    # Take widest gutters as the most likely column separators
    if len(gutters) > num_columns + 1:
        gutters = sorted(gutters, key=lambda g: g[1] - g[0], reverse=True)
        gutters = gutters[: num_columns + 1]
        gutters.sort(key=lambda g: (g[0] + g[1]) / 2)

    columns = []
    for i in range(num_columns):
        x_left = gutters[i][1]  # right edge of preceding gutter
        x_right = gutters[i + 1][0]  # left edge of following gutter
        columns.append((x_left, x_right))

    return columns


def ocr_words(page: np.ndarray) -> list[dict]:
    """Run Tesseract and return one dict per detected word with bbox + confidence.

    Uses both PSM 11 (sparse text) and PSM 6 (uniform block) and takes the
    union — each mode detects entry words the other misses. Duplicates
    (same text within a few pixels) are deduplicated.
    """
    img = Image.fromarray(page)

    def collect(config: str) -> list[dict]:
        data = pytesseract.image_to_data(
            img, output_type=pytesseract.Output.DICT, config=config
        )
        out = []
        for i in range(len(data["text"])):
            text = data["text"][i].strip()
            try:
                conf = float(data["conf"][i])
            except (TypeError, ValueError):
                conf = -1
            if not text or conf < 50:
                continue
            out.append(
                {
                    "text": text,
                    "x0": data["left"][i],
                    "y0": data["top"][i],
                    "x1": data["left"][i] + data["width"][i],
                    "y1": data["top"][i] + data["height"][i],
                    "conf": conf,
                }
            )
        return out

    words = collect("--psm 11") + collect("--psm 6")

    # Deduplicate: if two detections share the same text and overlap heavily,
    # keep the one with higher confidence.
    words.sort(key=lambda w: -w["conf"])
    deduped: list[dict] = []
    for w in words:
        keep = True
        for d in deduped:
            if d["text"] != w["text"]:
                continue
            # Box-overlap test
            ix0 = max(d["x0"], w["x0"])
            iy0 = max(d["y0"], w["y0"])
            ix1 = min(d["x1"], w["x1"])
            iy1 = min(d["y1"], w["y1"])
            if ix1 > ix0 and iy1 > iy0:
                inter = (ix1 - ix0) * (iy1 - iy0)
                area_w = (w["x1"] - w["x0"]) * (w["y1"] - w["y0"])
                if area_w > 0 and inter / area_w > 0.5:
                    keep = False
                    break
        if keep:
            deduped.append(w)
    return deduped


def filter_entries(
    words: list[dict],
    columns: list[tuple[int, int]],
    label_margin_frac: float = 0.20,
) -> list[dict]:
    """
    Keep only words that are likely entry-word labels:
      - lowercase, alphabetic
      - inside a column
      - NEAR the column's content-left edge (i.e. directly after the leading
        "1 "/"2 " number)
      - NOT inside the title or a section header (filtered by font height heuristic)

    `label_margin_frac` is a fraction of column width — entry words must
    start within this distance of the leftmost word actually present in the
    column. We anchor to the leftmost-word position rather than the raw
    column gutter, because pages often have substantial padding between
    the gutter and the start of column content.
    """
    if not words:
        return []

    # Estimate body-text height from the median word height.
    heights = sorted(w["y1"] - w["y0"] for w in words)
    median_h = heights[len(heights) // 2]

    # For each column, find the dominant ENTRY-word x position. We restrict
    # to lowercase words ≥3 chars so leading enumeration numbers, uppercase
    # headers ("FORMS", "WORDS"), and other non-entry text don't pull
    # content_left too far left.
    col_content_left: list[int] = []
    bin_size = max(5, int(np.median(heights) / 3)) if heights else 10
    for cx0, cx1 in columns:
        in_col_xs = [
            w["x0"]
            for w in words
            if cx0 <= w["x0"] < cx1
            and len(w["text"]) >= 3
            and w["text"].islower()
        ]
        if not in_col_xs:
            col_content_left.append(cx0)
            continue
        bins: dict[int, int] = {}
        for x in in_col_xs:
            key = (x // bin_size) * bin_size
            bins[key] = bins.get(key, 0) + 1
        # Take the leftmost bin with count >= 3 (i.e. shared by multiple rows)
        leftmost_solid = min((k for k, v in bins.items() if v >= 3), default=min(bins))
        col_content_left.append(leftmost_solid)

    kept = []
    for w in words:
        text = w["text"]
        if not WORD_RE.match(text):
            continue
        if text in STOPWORDS:
            continue

        # Find which column this word is in
        col_idx = None
        for i, (cx0, cx1) in enumerate(columns):
            if cx0 <= w["x0"] < cx1:
                col_idx = i
                break
        if col_idx is None:
            continue

        cx0, cx1 = columns[col_idx]
        col_w = cx1 - cx0
        content_left = col_content_left[col_idx]
        # Must start within label_margin_frac of the content-left edge
        if w["x0"] - content_left > col_w * label_margin_frac:
            continue

        # Sub-label rejection: if this word's x0 is much further right than
        # the dominant entry-word x0 in this column, it's an indented italic
        # sub-label (e.g. "1 cause" under "1 because") and has no shorthand.
        # We allow up to ~half a body-text-height of slop.
        if w["x0"] - content_left > median_h * 0.6:
            continue

        # Skip if word is much taller than typical body text (a section header).
        if (w["y1"] - w["y0"]) > median_h * 2.0:
            continue

        w = dict(w)
        w["col_idx"] = col_idx
        w["col_x0"] = cx0
        w["col_x1"] = cx1
        kept.append(w)

    return kept


def remove_sublabels(entries: list[dict]) -> list[dict]:
    """
    Sub-labels are entries that don't have their own shorthand — they sit
    underneath a parent word and reference its form. They typically:
      - appear directly below another entry (small y-gap)
      - are slightly indented further right than the parent
      - have NO substantial ink to their right (no shorthand on that line)
    We use the third property because it's the most reliable.
    Caller filters those out using the shorthand-detection pass.
    """
    # Sort by (column, y)
    return sorted(entries, key=lambda e: (e["col_idx"], e["y0"]))


def find_shorthand_bbox(
    page: np.ndarray,
    word_box: dict,
    *,
    pad_y_frac: float = 0.4,
    gap_after_word_frac: float = 0.4,
    min_blob_area_frac: float = 0.0001,
    cluster_gap_frac: float = 0.8,
) -> tuple[int, int, int, int] | None:
    """
    Crop the shorthand stroke that appears to the right of the given word.

    Strategy: take a horizontal slice from just past the word's right edge to
    the column's right edge, vertically padded. Within that slice, find
    connected components, drop tiny noise, group by horizontal gaps, and pick
    the rightmost cluster.

    All thresholds scale with the word's height so the function works at any
    DPI and any page size.
    """
    h, w = page.shape
    word_h = word_box["y1"] - word_box["y0"]

    pad_y = int(word_h * pad_y_frac)
    gap_after_word = int(word_h * gap_after_word_frac)
    cluster_gap = int(word_h * cluster_gap_frac)
    min_blob_area = max(8, int(word_h * word_h * min_blob_area_frac))

    y0 = max(0, word_box["y0"] - pad_y)
    y1 = min(h, word_box["y1"] + pad_y)
    x0 = min(w, word_box["x1"] + gap_after_word)
    x1 = word_box["col_x1"]

    if x1 - x0 < word_h or y1 - y0 < 5:
        return None

    region = (page[y0:y1, x0:x1] < 150).astype(np.uint8)
    if region.sum() == 0:
        return None

    nlab, _, stats, _ = cv2.connectedComponentsWithStats(region, connectivity=8)
    blobs = []
    for i in range(1, nlab):
        x, y, ww, hh, area = stats[i]
        if area < min_blob_area:
            continue
        blobs.append((int(x), int(y), int(ww), int(hh), int(area)))
    if not blobs:
        return None

    # Group blobs into clusters separated by horizontal gaps >= cluster_gap.
    blobs.sort(key=lambda b: b[0])
    clusters: list[list] = [[blobs[0]]]
    max_right = blobs[0][0] + blobs[0][2]
    for i in range(1, len(blobs)):
        b = blobs[i]
        if b[0] - max_right >= cluster_gap:
            clusters.append([b])
        else:
            clusters[-1].append(b)
        max_right = max(max_right, b[0] + b[2])

    # Walk clusters right-to-left, returning the first one with substantial ink.
    # This skips over isolated noise specs at the far right.
    substantial_threshold = min_blob_area * 2
    cluster = None
    for c in reversed(clusters):
        if any(b[4] >= substantial_threshold for b in c):
            cluster = c
            break
    if cluster is None:
        # No cluster contains substantial ink — likely a sub-label row.
        return None

    bx0 = min(b[0] for b in cluster)
    by0 = min(b[1] for b in cluster)
    bx1 = max(b[0] + b[2] for b in cluster)
    by1 = max(b[1] + b[3] for b in cluster)

    pad = max(8, int(word_h * 0.3))
    return (
        max(0, x0 + bx0 - pad),
        max(0, y0 + by0 - pad),
        min(w, x0 + bx1 + pad),
        min(h, y0 + by1 + pad),
    )


def to_transparent(crop: Image.Image, threshold: int = 240) -> Image.Image:
    """
    Convert a grayscale page crop to RGBA where the white paper becomes
    transparent and the ink stays opaque black.

    The grayscale value of each pixel is mapped to alpha: dark pixels (ink)
    become opaque, light pixels (paper) become transparent. Pixels above
    `threshold` are forced to fully transparent so faint scanner haze in the
    paper background doesn't appear as a translucent gray haze.

    Anti-aliased stroke edges are preserved because intermediate gray values
    map to intermediate alpha values.
    """
    gray = np.array(crop.convert("L"), dtype=np.uint8)

    # alpha = 255 for pure black ink, 0 for pure white paper, smooth in between.
    # Then force everything above `threshold` to fully transparent.
    alpha = 255 - gray
    alpha[gray >= threshold] = 0

    # Build a black RGBA image; only alpha varies.
    h, w = gray.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 3] = alpha  # R, G, B already 0

    return Image.fromarray(rgba, mode="RGBA")


def save_unique(image: Image.Image, base: str, outdir: Path, counts: Counter) -> Path:
    """Save image as <base>.png; if name taken, suffix _2, _3, ..."""
    counts[base] += 1
    n = counts[base]
    name = f"{base}.png" if n == 1 else f"{base}_{n}.png"
    path = outdir / name
    image.save(path)
    return path


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def process_page(
    pdf_path: Path,
    page_idx: int,
    outdir: Path,
    counts: Counter,
    dpi: int,
) -> tuple[int, int]:
    """Returns (extracted_count, skipped_count) for one page."""
    page = render_page(pdf_path, page_idx, dpi)
    columns = detect_columns(page, num_columns=3)
    log.debug("Page %d columns: %s", page_idx + 1, columns)

    words = ocr_words(page)
    entries = filter_entries(words, columns)
    entries = remove_sublabels(entries)

    pil_page = Image.fromarray(page)
    extracted = 0
    skipped = 0
    for entry in entries:
        bbox = find_shorthand_bbox(page, entry)
        if bbox is None:
            log.debug(
                "Page %d: no shorthand for %r at y=%d (sub-label?)",
                page_idx + 1,
                entry["text"],
                entry["y0"],
            )
            skipped += 1
            continue
        crop = pil_page.crop(bbox)
        crop = to_transparent(crop)
        save_unique(crop, entry["text"], outdir, counts)
        extracted += 1
    return extracted, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pdf", type=Path, help="Path to the PDF file")
    parser.add_argument("outdir", type=Path, help="Directory to write PNGs into")
    parser.add_argument("--dpi", type=int, default=300, help="Render DPI (default 300)")
    parser.add_argument("--start", type=int, default=1, help="First page to process (1-indexed)")
    parser.add_argument("--end", type=int, default=None, help="Last page to process (inclusive, 1-indexed)")
    parser.add_argument(
        "--tesseract-cmd",
        default=None,
        help="Path to tesseract.exe if not on PATH",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = args.tesseract_cmd

    if not args.pdf.is_file():
        log.error("PDF not found: %s", args.pdf)
        sys.exit(1)
    args.outdir.mkdir(parents=True, exist_ok=True)

    with fitz.open(args.pdf) as doc:
        total_pages = doc.page_count
    end = args.end or total_pages

    log.info("Processing pages %d..%d of %s (total %d)", args.start, end, args.pdf.name, total_pages)

    counts: Counter = Counter()
    grand_extracted = 0
    grand_skipped = 0
    for page_num in range(args.start, end + 1):
        try:
            ext, skp = process_page(args.pdf, page_num - 1, args.outdir, counts, args.dpi)
        except Exception as exc:
            log.exception("Page %d failed: %s", page_num, exc)
            continue
        grand_extracted += ext
        grand_skipped += skp
        log.info("Page %d: extracted %d, skipped %d", page_num, ext, skp)

    log.info(
        "Done. %d files written to %s. %d sub-label rows skipped.",
        grand_extracted,
        args.outdir,
        grand_skipped,
    )


if __name__ == "__main__":
    main()
