import json
import re
from pathlib import Path
from pypdf import PdfReader


def apply_gst_rules(raw_gst: str) -> str:
    # 1. Trim whitespace
    gst = raw_gst.strip()

    # 2. Sequential replacements
    replacements = [
        ("oo", "u"),
        ("md", "mt"),
        ("ten", "tn"),
        ("left s", "s2"),
        ("over th", "th1"),
        ("under th", "th2"),
        ("ing", "h"),
        ("ia", "ea"),
        ("ted", "td"),
        ("oi", "o-e"),
        ("î", "i"),
        ("ngk", "nk"),
    ]

    for old, new in replacements:
        gst = gst.replace(old, new)

    # 3. Replace spaces with '/'
    gst = gst.replace(" ", "/")
    return gst


def parse_pdf_to_json(pdf_path: str, output_json_path: str):
    if not Path(pdf_path).is_file():
        print(
            "PDF not found. Please place 'Gregg Notehand Dictionary (1960).pdf' "
            "in the same folder as this script."
        )
        return

    reader = PdfReader(pdf_path)

    # Regex pattern matching: [text], [gst_raw] ([notes])
    # Group 1: Text before first comma
    # Group 2: Raw GST shorthand text
    # Group 3: Full parenthesis group (notes)
    pattern = re.compile(r"^([^,]+),\s*([^\(]+?)\s*(\([^\)]+\))$")

    json_objects = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue

        for line in text.splitlines():
            line = line.strip()

            # Ignore empty lines or non-matching format lines
            match = pattern.match(line)
            if not match:
                continue

            word_text = match.group(1).strip()
            raw_gst = match.group(2)
            notes = match.group(3).strip()

            transformed_gst = apply_gst_rules(raw_gst)

            json_objects.append(
                {"text": word_text, "gst": transformed_gst, "notes": notes}
            )

    # Write results to output file
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_objects, f, ensure_ascii=False, indent=2)

    print(
        f"Successfully extracted {len(json_objects)} objects to '{output_json_path}'."
    )


# Usage
script_dir = Path(__file__).resolve().parent
pdf_file = script_dir / "Gregg Notehand Dictionary (1960).pdf"
output_file = script_dir / "NoteDictionary.json"

parse_pdf_to_json(str(pdf_file), str(output_file))