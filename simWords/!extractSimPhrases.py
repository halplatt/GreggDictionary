"""Extract the shorthand outline of every phrase on the simPhrases pages.

For each phrase writes into this folder:
  <phrase>.png  outline on a transparent background
  <phrase>.txt  pixels the outline extends below the line of writing (>= 0)
"""
import os
import re
import sys
from collections import Counter

import numpy as np
import pytesseract
from PIL import Image
import cv2

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "simDictionary", "simPhrases")
OUT = HERE

INK_THR = 150          # gray level below which a pixel is ink
SCALE = 2              # OCR upscaling
SPLIT = 0.485          # column split used for OCR only
SHORT2 = set("a i am an as at be by do go he if in is it me my no of on or so to up us we mr mrs".split())
WORD_RE = re.compile(r"^[A-Za-z][A-Za-z.,'\-]*$|^I$")
BAD_CHARS = re.compile(r'[<>:"/\\|?*]')


def ocr_column(gray, x_off, x_end):
    """Return list of lines: dict(words=[(text,l,t,r,b)], ...) in page coords."""
    crop = Image.fromarray(gray[:, x_off:x_end])
    crop = crop.resize((crop.width * SCALE, crop.height * SCALE), Image.LANCZOS)
    d = pytesseract.image_to_data(crop, config="--psm 6", output_type=pytesseract.Output.DICT)
    lines = {}
    for i, t in enumerate(d["text"]):
        if not t.strip():
            continue
        key = (d["block_num"][i], d["par_num"][i], d["line_num"][i])
        l = d["left"][i] / SCALE + x_off
        tp = d["top"][i] / SCALE
        lines.setdefault(key, []).append(
            (t.strip(), l, tp, l + d["width"][i] / SCALE, tp + d["height"][i] / SCALE, float(d["conf"][i])))
    res = []
    for ws in lines.values():
        ws.sort(key=lambda w: w[1])
        res.append(ws)
    return res


def is_junk(t):
    s = t.strip(".,")
    if s == "I" or not s:
        return not s
    return (len(s) <= 2 and s.lower() not in SHORT2) or (len(s) >= 2 and s.isupper())


def fix_text(t):
    t = re.sub(r"^(?:[lLTJ1|]) ", "I ", t)
    t = re.sub(r"^l(am|have|had|can|could|will|do|did|would|shall)\b", r"I \1", t)
    t = re.sub(r"(?<= )[lLTJ|] (?=[a-z])", "I ", t)
    words = t.split()
    while len(words) > 1 and is_junk(words[-1]):
        words.pop()
    return " ".join(words)


def clean_line(ws, x0):
    """Keep the leading run of text words; outline junk is recognised by its width per character."""
    keep = []
    for t, l, tp, r, b, conf in ws:
        if not WORD_RE.match(t) or (r - l) / len(t) > 17:
            break
        keep.append((t, l, tp, r, b, conf))
    while keep and is_junk(keep[-1][0]):
        keep.pop()
    return keep


def reocr_line(gray, l, tp, r, b, fallback):
    pad = 6
    crop = gray[max(0, int(tp) - pad):int(b) + pad, max(0, int(l) - pad):int(r) + pad]
    crop = np.pad(crop, 10, constant_values=255)
    im = Image.fromarray(crop)
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    txt = pytesseract.image_to_string(im, config="--psm 7").strip()
    txt = re.sub(r"\s+", " ", txt)
    txt = fix_text(txt.replace("\u2019", "'").replace("\u2018", "'").replace("`", "'"))
    return txt if re.match(r"^[A-Za-z][A-Za-z.,'\- ]*$", txt) else fix_text(fallback)

def text_baseline(ink, l, r, top, bot):
    band = ink[max(0, int(top) - 4):int(bot) + 6, int(l):int(r)]
    prof = band.sum(axis=1).astype(float)
    if prof.max() == 0:
        return bot
    ys = np.where(prof >= 0.3 * prof.max())[0]
    return max(0, int(top) - 4) + ys.max()


def build_grid(ink, mode, x_end, lines):
    """Turn OCR lines into regularly spaced rows, recovering rows OCR missed."""
    ents = []
    for ws in lines:
        l = min(x[1] for x in ws)
        r = max(x[3] for x in ws)
        tp = min(x[2] for x in ws)
        b = max(x[4] for x in ws)
        ents.append(((tp + b) / 2, l, r, tp, b, " ".join(x[0] for x in ws)))
    short = {i for i, ws in enumerate(lines) if len(ws) < 2}
    ents.sort()
    if len(ents) < 2:
        return [e[1:] for e in ents]
    diffs = [b[0] - a[0] for a, b in zip(ents, ents[1:]) if 30 < b[0] - a[0] < 60]
    if not diffs:
        return [e[1:] for e in ents]
    pitch = float(np.median(diffs))
    h = ink.shape[0]

    def has_ink(y):
        y = int(y)
        if not 0 <= y < h:
            return False
        blk = ink[max(0, y - 10):y + 10, max(0, int(mode) - 2):int(mode) + 40]
        return blk.sum() > 25 and blk.sum(axis=1).max() < 34

    def snap(y, used_ids):
        for k, e in enumerate(ents):
            if k not in used_ids and abs(e[0] - y) < pitch * 0.35:
                return k
        return None

    def synth(y):
        y = int(y)
        win = ink[max(0, y - int(pitch * 0.45)):y + int(pitch * 0.45), max(0, int(mode) - 2):int(mode) + 60].sum(axis=1)
        idx = np.nonzero(win >= 2)[0]
        if len(idx):
            y = max(0, y - int(pitch * 0.45)) + (int(idx.min()) + int(idx.max())) // 2
        band = ink[max(0, y - 12):y + 12, int(mode) - 2:int(x_end)].any(axis=0)
        last, gap = 0, 0
        for x, v in enumerate(band):
            if v:
                last, gap = x, 0
            else:
                gap += 1
                if gap > 22:
                    break
        return (mode, mode - 2 + last + 1, y - 14, y + 14, "")

    def fixed(e):
        if len(e[5].split()) < 2:
            sy = synth(e[0])
            return (e[1], sy[1], sy[2], sy[3], e[5])
        return e[1:]

    used_ids = set()
    out = []
    k0 = snap(ents[0][0], used_ids)
    used_ids.add(k0)
    out.append(fixed(ents[k0]))
    for direction in (-1, 1):
        y = ents[0][0]
        while True:
            y += direction * pitch
            k = snap(y, used_ids)
            if k is not None:
                used_ids.add(k)
                y = ents[k][0]
                out.append(fixed(ents[k]))
            elif has_ink(y):
                out.append(synth(y))
            else:
                # tolerate one blank row before giving up only when further detected lines exist
                if not any((e[0] - y) * direction > 0 and abs(e[0] - y) < pitch * 1.5 for i, e in enumerate(ents) if i not in used_ids):
                    break
    return out

def assign_outlines(outline_ink, rows, w):
    """Label every outline pixel with its row index + 1 (0 = background / unassigned).

    Each row gets a seed at the left end of its outline; labels then flood along the ink so that
    outlines touching their neighbours are split roughly half way between seeds.
    """
    h = outline_ink.shape[0]
    lab = np.zeros((h, outline_ink.shape[1]), np.float32)
    right_l = [r_["l"] for r_ in rows if r_["l"] > w * 0.4]
    col_split = min(right_l) - 2 if right_l else w
    for ri, row in enumerate(rows):
        x_lo = int(row["r"]) + 2
        x_hi = int(row["r"]) + 110
        if row["l"] <= w * 0.4:
            x_hi = min(x_hi, int(col_split))
        y_lo, y_hi = int(row["base"]) - 22, int(row["base"]) + 12
        reg = outline_ink[max(0, y_lo):y_hi, x_lo:x_hi]
        ys, xs = np.nonzero(reg)
        if len(xs) < 8:
            continue
        k = int(np.argmin(xs * 3 + np.abs(ys + max(0, y_lo) - (row["base"] - 8))))
        lab[ys[k] + max(0, y_lo), xs[k] + x_lo] = ri + 1
    kern = np.ones((3, 3), np.uint8)
    inkf = outline_ink.astype(np.float32)
    for _ in range(600):
        grown = cv2.dilate(lab, kern)
        new = (lab == 0) & (grown > 0) & outline_ink
        if not new.any():
            break
        lab[new] = grown[new]
    # parts disconnected from every seed (dots, detached strokes) join the nearest labelled row
    n, cc, stats, _ = cv2.connectedComponentsWithStats(outline_ink.astype(np.uint8), connectivity=8)
    ly, lx = np.nonzero(lab)
    if len(ly):
        lv = lab[ly, lx]
        for c in range(1, n):
            if stats[c, cv2.CC_STAT_AREA] < 25:
                continue
            sel = cc == c
            if (lab[sel] > 0).any():
                continue
            py, px = np.nonzero(sel)
            best_d, best_l = 1e9, 0
            for s in range(0, len(py), 200):
                d = np.hypot(py[s:s + 200, None] - ly[None, :], px[s:s + 200, None] - lx[None, :])
                j = np.unravel_index(np.argmin(d), d.shape)
                if d[j] < best_d:
                    best_d, best_l = d[j], lv[j[1]]
            if best_d < 45:
                lab[sel] = best_l
    return lab.astype(np.int32)

def process_page(path, used):
    img = Image.open(path).convert("L")
    gray = np.array(img)
    h, w = gray.shape
    ink = gray < INK_THR
    bg = np.percentile(gray, 90)

    cols = []
    sp = int(w * SPLIT)
    for x_off, x_end in ((0, sp), (sp, w)):
        raw = ocr_column(gray, x_off, x_end)
        starts = Counter(int(round(f[1] / 8)) for f in (next((x for x in ws if WORD_RE.match(x[0]) and x[5] > 50), None) for ws in raw) if f)
        if not starts:
            continue
        mode = starts.most_common(1)[0][0] * 8
        lines = []
        for ws in raw:
            ws = [x for x in ws if x[1] > mode - 12]
            if not ws or abs(ws[0][1] - mode) > 12:
                continue
            keep = clean_line(ws, mode)
            if keep:
                lines.append(keep)
        cols.append(build_grid(ink, mode, x_end, lines))

    # text mask / row info
    text_mask = np.zeros_like(ink)
    rows = []
    for ents in cols:
        for l, r, tp, b, fb in ents:
            text_mask[max(0, int(tp) - 3):int(b) + 4, max(0, int(l) - 2):int(r) + 3] = True
            base = text_baseline(ink, l, r, tp, b)
            rows.append(dict(phrase=reocr_line(gray, l, tp, r, b, fb), l=l, r=r, base=base, comps=[]))
    rows.sort(key=lambda d: (d["l"] > w * 0.4, d["base"]))
    right_l = [r_["l"] for r_ in rows if r_["l"] > w * 0.4]
    col_split = min(right_l) - 2 if right_l else w

    outline_ink = ink & ~text_mask
    lab = assign_outlines(outline_ink, rows, w)

    results = 0
    for ri, row in enumerate(rows):
        mask0 = lab == ri + 1
        if mask0.sum() < 25:
            continue
        mask = cv2.dilate(mask0.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        mask &= ~text_mask & ((lab == 0) | mask0)
        ys, xs = np.where(mask)
        t, b, l, r = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sub = gray[t:b, l:r].astype(float)
        a = np.clip((bg - sub) / max(bg - 20, 1), 0, 1) * 255
        a = np.where(mask[t:b, l:r], a, 0).astype(np.uint8)
        rgba = np.zeros(a.shape + (4,), np.uint8)
        rgba[..., 3] = a
        depth = max(0, int(b - 1 - row["base"]))
        name = BAD_CHARS.sub("", row["phrase"]).strip().rstrip(".").strip()
        name = re.sub(r"\s+", " ", name)
        if not name:
            print("  unreadable phrase, skipped")
            continue
        base_name, k = name, 2
        while name.lower() in used:
            name = f"{base_name} ({k})"
            k += 1
        used.add(name.lower())
        Image.fromarray(rgba, "RGBA").save(os.path.join(OUT, name + ".png"))
        with open(os.path.join(OUT, name + ".txt"), "w") as f:
            f.write(str(depth))
        results += 1
    return results, len(rows)


def main():
    files = sorted(f for f in os.listdir(SRC) if f.lower().endswith(".png"))
    if len(sys.argv) > 1:
        files = files[:int(sys.argv[1])]
    used = set()
    total = 0
    for f in files:
        n, rows = process_page(os.path.join(SRC, f), used)
        total += n
        print(f"{f}: {n} outlines / {rows} text lines")
    print("total", total)


if __name__ == "__main__":
    main()

