import os
import re
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

folder = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(folder, "indexSimPhrases.txt")


SHORT_WORDS = set(
    "a i an as at be by do go he if in is it me my no of on or so to up us we am ad "
    "act add age ago aid aim air all and any are arm art ask bad bag bed big bit box boy bus but buy can car cut day did die dog dry due ear eat end era eye far fee few fit fix for fun gas get god got guy had has her hey him his hit hot how its job key kid law lay led leg let lie lot low mad man map may men mix mr mrs new nor not now odd off oil old one our out own pay per put raw red rid run say sea see set she sir six sky son sum sun tax tea ten the tie tip too top try two use van via war was way who why win yes yet you".split()
)


# Manual corrections for pages where the scan was too noisy for OCR (checked by eye).
OVERRIDES = {
    12: "at the time", 13: "back and forth", 20: "face to face", 23: "from time",
    28: "he let", 31: "I am", 33: "I got", 37: "if it", 39: "if you must be",
    43: "it is the", 53: "please ship the", 58: "take care", 65: "to enclose",
    66: "to him", 67: "to post", 78: "we will show", 88: "your request",
}


def ocr_lines(img, scale, thr):
    w, h = img.size
    # Left column only; the right column's phrases are never first.
    col = img.crop((0, 0, int(w * 0.46), h))
    col = col.resize((col.width * scale, col.height * scale), Image.LANCZOS)
    if thr:
        col = col.point(lambda v: 255 if v > thr else 0)
    data = pytesseract.image_to_data(col, config="--psm 6", output_type=pytesseract.Output.DICT)
    lines = {}
    for i, txt in enumerate(data["text"]):
        if not txt.strip():
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        lines.setdefault(key, []).append(
            (data["left"][i] // scale, data["top"][i] // scale, txt, float(data["conf"][i])))
    rows = []
    for words in lines.values():
        words.sort()
        rows.append((min(t for _, t, _, _ in words), words))
    rows.sort(key=lambda r: r[0])
    return rows


def first_phrase(path):
    img = Image.open(path).convert("L")
    w, h = img.size
    for scale, thr in ((1, 0), (2, 0), (2, 150), (2, 110)):
        for top, words in ocr_lines(img, scale, thr):
            # Entries start flush left; headings are centered/indented.
            if words[0][0] > w * 0.12 or top < 5:
                continue
            toks = []
            for _, _, t, c in words:
                # Stop at the first low-confidence token: it's shorthand outline noise.
                if c < 45 or not re.fullmatch(r"[A-Za-z.'\-]+", t):
                    break
                toks.append(t)
            # Trailing 1-3 letter tokens that aren't real words are outline noise.
            while len(toks) > 1 and len(toks[-1]) <= 3 and toks[-1].lower().strip(".") not in SHORT_WORDS:
                toks.pop()
            text = " ".join(toks)
            if len(text) < 2 or text.isupper() or re.search(r"PHRASES|GREGG|SHORTHAND", text, re.I):
                continue
            return text
    return ""


with open(out_path, "w", encoding="utf-8") as f:
    for n in range(4, 89):
        name = f"sp_Page_{n:03d}"
        p = os.path.join(folder, name + ".png")
        if not os.path.exists(p):
            continue
        phrase = OVERRIDES.get(n) or first_phrase(p)
        f.write(f"{name},{phrase}\n")
        print(name, phrase)


