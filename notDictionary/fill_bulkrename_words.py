from __future__ import annotations

import re
from pathlib import Path
from pypdf import PdfReader


ENTRY_PREFIX_RE = re.compile(r"^([^,(][^,(]*?),\s")


def extract_word_for_page(page_text: str, page_number: int) -> str:
    # Dictionary introduction page: use the top letter marker.
    if page_number == 3:
        return "a"

    lines = [ln.strip() for ln in page_text.splitlines() if ln.strip()]

    # Drop trailing page number lines like "149".
    while lines and lines[-1].isdigit():
        lines.pop()

    if not lines:
        return ""

    first_line = lines[0]

    # Normal case: first line starts with "word, ...".
    entry_match = ENTRY_PREFIX_RE.match(first_line)
    if entry_match:
        return entry_match.group(1).strip().lower()

    # Section divider pages start with patterns like "CC", "DD", "SS-Z", "XX:", "ZZ-S".
    m = re.search(r"[A-Za-z]", first_line)
    return m.group(0).lower() if m else ""


def main() -> None:
    base = Path(__file__).resolve().parent
    csv_path = base / "_BulkRename_words.csv"
    pdf_path = base / "Gregg Notehand Dictionary (1960).pdf"

    rows = csv_path.read_text(encoding="utf-8").splitlines()
    reader = PdfReader(str(pdf_path))

    updated_rows: list[str] = []

    for row in rows:
        if not row.strip():
            continue

        if "," not in row:
            updated_rows.append(row)
            continue

        image_name, _existing_word = row.split(",", 1)

        if not image_name.strip():
            continue

        m = re.search(r"_Page_(\d{3})$", image_name)
        if not m:
            # Keep malformed/unexpected rows untouched.
            updated_rows.append(row)
            continue

        page_number = int(m.group(1))
        page_index = page_number - 1

        if page_index < 0 or page_index >= len(reader.pages):
            updated_rows.append(f"{image_name},")
            continue

        page_text = reader.pages[page_index].extract_text() or ""
        word = extract_word_for_page(page_text, page_number)
        updated_rows.append(f"{image_name},{word}")

    csv_path.write_text("\n".join(updated_rows) + "\n", encoding="utf-8")
    print(f"Updated {csv_path}")


if __name__ == "__main__":
    main()
