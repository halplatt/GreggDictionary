#!/usr/bin/env python3
"""Update notes links in !searchGSText.json.

For each object, if the notes field contains tokens like #74,
replace each token with:
../notManual/!searchPages.html?p74&tab=mn1&disp=p74
"""

from __future__ import annotations

import json
import re
from pathlib import Path

URL_TEMPLATE = "../notManual/!searchPages.html?{pnum}&tab=mn1&disp={pnum}"
HASH_PAGE_RE = re.compile(r"#(\d+)")


def replace_hash_pages(notes: str) -> tuple[str, int]:
    """Replace #<digits> with the URL template, returning new text and count."""

    replacements = 0

    def _sub(match: re.Match[str]) -> str:
        nonlocal replacements
        replacements += 1
        pnum = f"p{match.group(1)}"
        return URL_TEMPLATE.format(pnum=pnum)

    return HASH_PAGE_RE.sub(_sub, notes), replacements


def update_file(json_path: Path) -> tuple[int, int]:
    """Update the JSON file in place.

    Returns:
        (objects_updated, total_replacements)
    """

    data = json.loads(json_path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError("Expected top-level JSON array")

    objects_updated = 0
    total_replacements = 0

    for item in data:
        if not isinstance(item, dict):
            continue

        notes = item.get("notes")
        if not isinstance(notes, str) or "#" not in notes:
            continue

        updated_notes, count = replace_hash_pages(notes)
        if count > 0 and updated_notes != notes:
            item["notes"] = updated_notes
            objects_updated += 1
            total_replacements += count

    json_path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return objects_updated, total_replacements


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    target = base_dir / "!searchGSText.json"

    objects_updated, total_replacements = update_file(target)
    print(f"Updated objects: {objects_updated}")
    print(f"Total # replacements: {total_replacements}")
    print(f"File updated: {target}")


if __name__ == "__main__":
    main()
