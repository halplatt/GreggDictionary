"""Extract shorthand outlines from simDictionary page scans.

Requires Pillow: py -m pip install Pillow
Run all pages: py !createpng.py
Run one page:  py !createpng.py --page abacus
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image

SOURCE_DIR = Path(r"D:\HostGatorFiles\public_html\notes\simDictionary")
OUTPUT_DIR = Path(r"D:\HostGatorFiles\public_html\notes\simWords")
REFERENCE_FILE = SOURCE_DIR / "!reference.json"
INK_THRESHOLD = 180
WORD_SCAN_HEIGHT = 16
ROW_PADDING = 3
MIN_OUTLINE_PIXELS = 6
WORD_END_GAP = 10
AVERAGE_LETTER_WIDTH = 19
FALLBACK_SEED_WIDTH = 250
TEXT_GAP_BRIDGE = 60
FRAGMENT_GAP_BRIDGE = 8
OUTLINE_OVERRIDES = {
    # page, word: source-image rectangle for outlines that overlap other entries.
    ("abacus", "abandonment"): [(348, 561, 607, 664)],
    ("abacus", "abdominal"): [(259, 1564, 363, 1621), (280, 1515, 797, 1573)],
}


def ink_mask(image: Image.Image) -> Image.Image:
    """Return a mask where non-white scan pixels are white."""
    grayscale = image.convert("L")
    return grayscale.point(lambda value: 255 if value < INK_THRESHOLD else 0)


def row_bounds(entries: list[dict], index: int, image_height: int) -> tuple[int, int]:
    """Use neighboring word positions in this column to bound one shorthand row."""
    center = entries[index]["y"]
    above = entries[index - 1]["y"] if index else max(0, center - 54)
    below = entries[index + 1]["y"] if index + 1 < len(entries) else min(image_height, center + 54)
    return max(0, round((above + center) / 2) - ROW_PADDING), min(
        image_height, round((center + below) / 2) + ROW_PADDING
    )


def last_printed_x(mask: Image.Image, word_x: int, word_y: int, scan_right: int | None = None) -> int | None:
    """Find the last letter by locating the first wide blank gap after the word."""
    top = max(0, round(word_y) - WORD_SCAN_HEIGHT // 2)
    bottom = min(mask.height, round(word_y) + WORD_SCAN_HEIGHT // 2)
    pixels = mask.load()
    seen_ink = False
    blank_run = 0
    last_ink = None

    for x in range(max(0, round(word_x) - 3), min(mask.width, scan_right or mask.width)):
        has_ink = any(pixels[x, y] == 255 for y in range(top, bottom))
        if has_ink:
            seen_ink = True
            blank_run = 0
            last_ink = x
        elif seen_ink:
            blank_run += 1
            if blank_run >= WORD_END_GAP:
                return last_ink
    return last_ink


def estimated_word_end(word_x: int, word: str, column_right: int) -> int:
    """Estimate a printed word's right edge when shorthand obscures its blank gap."""
    return min(column_right - 1, word_x + max(70, len(word) * AVERAGE_LETTER_WIDTH))


def ink_bbox(mask: Image.Image, left: int, top: int, right: int, bottom: int) -> tuple[int, int, int, int] | None:
    """Return the bounding box of ink in a rectangular area."""
    bbox = mask.crop((left, top, right, bottom)).getbbox()
    if bbox is None:
        return None
    return left + bbox[0], top + bbox[1], left + bbox[2], top + bbox[3]


def text_ink_pixels(mask: Image.Image, entries: list[dict]) -> set[tuple[int, int]]:
    """Identify printed-word ink so cross-column strokes cannot absorb letters."""
    pixels = mask.load()
    text_pixels: set[tuple[int, int]] = set()
    for entry in entries:
        word_x, word_y = round(entry["x"]), round(entry["y"])
        word_end = last_printed_x(mask, word_x, word_y)
        if word_end is None:
            continue
        for y in range(max(0, word_y - WORD_SCAN_HEIGHT // 2), min(mask.height, word_y + WORD_SCAN_HEIGHT // 2)):
            for x in range(max(0, word_x - 3), word_end + 1):
                if pixels[x, y] == 255:
                    text_pixels.add((x, y))
    return text_pixels


def outline_components(
    mask: Image.Image, left: int, row_top: int, row_bottom: int, right: int, text_pixels: set[tuple[int, int]]
) -> list[tuple[tuple[int, int, int, int], set[tuple[int, int]]]]:
    """Find ink components seeded in this outline cell, including cross-column strokes."""
    pixels = mask.load()
    seed_points = [
        (x, y)
        for y in range(row_top, row_bottom)
        for x in range(left, right)
        if pixels[x, y] == 255 and (x, y) not in text_pixels
    ]
    visited: set[tuple[int, int]] = set()
    components: list[tuple[tuple[int, int, int, int], set[tuple[int, int]]]] = []

    for seed in seed_points:
        if seed in visited:
            continue
        stack = [seed]
        visited.add(seed)
        min_x = max_x = seed[0]
        min_y = max_y = seed[1]
        pixel_count = 0
        component_pixels: set[tuple[int, int]] = set()
        while stack:
            x, y = stack.pop()
            pixel_count += 1
            component_pixels.add((x, y))
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            for next_x, next_y in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if (
                    left <= next_x < mask.width
                    and 0 <= next_y < mask.height
                    and (next_x, next_y) not in visited
                    and (next_x, next_y) not in text_pixels
                    and pixels[next_x, next_y] == 255
                ):
                    visited.add((next_x, next_y))
                    stack.append((next_x, next_y))
        if pixel_count >= MIN_OUTLINE_PIXELS:
            components.append(((min_x, min_y, max_x + 1, max_y + 1), component_pixels))
    return sorted(components, key=lambda component: (component[0][0], component[0][1]))


def merge_text_separated_components(
    components: list[tuple[tuple[int, int, int, int], set[tuple[int, int]]]], text_pixels: set[tuple[int, int]]
) -> list[tuple[tuple[int, int, int, int], set[tuple[int, int]]]]:
    """Join outline fragments when intervening printed text is their only separation."""
    merged = []
    while components:
        bbox, pixels = components.pop(0)
        changed = True
        while changed:
            changed = False
            left, top, right, bottom = bbox
            for index, (other_bbox, other_pixels) in enumerate(components):
                other_left, other_top, other_right, other_bottom = other_bbox
                gap_left, gap_right = sorted((right, other_left))
                overlaps_vertically = max(top, other_top) < min(bottom, other_bottom)
                nearby_fragments = (
                    overlaps_vertically
                    and min(abs(x - other_x) + abs(y - other_y) for x, y in pixels for other_x, other_y in other_pixels)
                    <= FRAGMENT_GAP_BRIDGE
                )
                has_text_between = any(
                    gap_left <= x < gap_right and max(top, other_top) <= y < min(bottom, other_bottom)
                    for x, y in text_pixels
                )
                if nearby_fragments or (
                    overlaps_vertically and gap_right - gap_left <= TEXT_GAP_BRIDGE and has_text_between
                ):
                    bbox = min(left, other_left), min(top, other_top), max(right, other_right), max(bottom, other_bottom)
                    pixels.update(other_pixels)
                    components.pop(index)
                    changed = True
                    break
        merged.append((bbox, pixels))
    return sorted(merged, key=lambda component: (component[0][0], component[0][1]))


def save_component(
    bbox: tuple[int, int, int, int], component_pixels: set[tuple[int, int]], output_name: str, text_bottom: int
) -> None:
    """Save one complete shorthand component and its descent measurement."""
    left, top, right, bottom = bbox
    source = Image.new("RGBA", (right - left, bottom - top), (255, 255, 255, 0))
    source_pixels = source.load()
    for x, y in component_pixels:
        source_pixels[x - left, y - top] = (0, 0, 0, 255)
    source.save(OUTPUT_DIR / f"{output_name}.png")
    descent = max(0, bbox[3] - text_bottom)
    (OUTPUT_DIR / f"{output_name}.txt").write_text(f"{descent}\n", encoding="ascii")


def override_component(
    mask: Image.Image, bbox: tuple[int, int, int, int], text_pixels: set[tuple[int, int]]
) -> set[tuple[int, int]]:
    """Return every non-text ink pixel inside a verified manual outline region."""
    left, top, right, bottom = bbox
    pixels = mask.load()
    return {
        (x, y)
        for y in range(top, bottom)
        for x in range(left, right)
        if pixels[x, y] == 255 and (x, y) not in text_pixels
    }


def save_outline(
    mask: Image.Image,
    entry: dict,
    row_top: int,
    row_bottom: int,
    column_right: int,
    text_pixels: set[tuple[int, int]],
    page_name: str,
) -> int:
    word = entry["t"]
    word_x, word_y = round(entry["x"]), round(entry["y"])
    word_end = last_printed_x(mask, word_x, word_y, column_right)
    if word_end is None:
        print(f"Skipped {word}: printed word was not found")
        return 0

    text_bbox = ink_bbox(
        mask,
        max(0, word_x - 3),
        max(0, word_y - WORD_SCAN_HEIGHT // 2),
        min(mask.width, word_end + 1),
        min(mask.height, word_y + WORD_SCAN_HEIGHT // 2),
    )
    override_bboxes = OUTLINE_OVERRIDES.get((page_name, word))
    if override_bboxes:
        saved = 0
        for index, override_bbox in enumerate(override_bboxes):
            component_pixels = override_component(mask, override_bbox, text_pixels)
            if text_bbox is None or not component_pixels:
                continue
            output_name = word.replace("/", "_").replace("\\", "_")
            component_name = output_name if index == 0 else f"{output_name}({index})"
            save_component(override_bbox, component_pixels, component_name, text_bbox[3])
            saved += 1
        if saved:
            return saved
    expected_word_end = estimated_word_end(word_x, word, column_right)
    outline_left = min(column_right, word_end + 1, expected_word_end + 1)
    components = outline_components(mask, outline_left, row_top, row_bottom, column_right, text_pixels)
    if not components:
        fallback_right = min(mask.width, column_right + FALLBACK_SEED_WIDTH)
        components = outline_components(mask, outline_left, row_top, row_bottom, fallback_right, text_pixels)
    components = merge_text_separated_components(components, text_pixels)
    if text_bbox is None or not components:
        print(f"Skipped {word}: no outline pixels found")
        return 0

    output_name = word.replace("/", "_").replace("\\", "_")
    for index, (bbox, component_pixels) in enumerate(components):
        component_name = output_name if index == 0 else f"{output_name}({index})"
        save_component(bbox, component_pixels, component_name, text_bbox[3])
    return len(components)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract shorthand outlines into transparent PNG files.")
    parser.add_argument("--page", help="Process only this source page name, without .png")
    args = parser.parse_args()

    pages = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    extracted = 0

    for page in pages:
        if args.page and page["page"] != args.page:
            continue
        image_path = SOURCE_DIR / f'{page["page"]}.png'
        if not image_path.exists():
            print(f"Skipped {page['page']}: page image is missing")
            continue
        image = Image.open(image_path)
        mask = ink_mask(image)
        columns: dict[float, list[dict]] = defaultdict(list)
        for entry in page["words"]:
            columns[entry["x"]].append(entry)
        text_pixels = text_ink_pixels(mask, page["words"])
        column_entries = [entries for _, entries in sorted(columns.items())]
        for column_index, entries in enumerate(column_entries):
            entries.sort(key=lambda entry: entry["y"])
            column_right = (
                round(column_entries[column_index + 1][0]["x"]) - 8
                if column_index + 1 < len(column_entries)
                else image.width
            )
            for index, entry in enumerate(entries):
                row_top, row_bottom = row_bounds(entries, index, image.height)
                extracted += save_outline(mask, entry, row_top, row_bottom, column_right, text_pixels, page["page"])

    print(f"Extracted {extracted} outlines to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()