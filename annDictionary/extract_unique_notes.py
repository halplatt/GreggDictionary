"""Extract a unique, sorted list of "notes" values from !searchGSText.json."""
import json
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "!searchGSText.json"
OUTPUT_FILE = Path(__file__).parent / "unique_notes.json"


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    unique_notes = sorted({entry.get("notes", "") for entry in data})

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(unique_notes, f, indent=4, ensure_ascii=False)

    print(f"Found {len(unique_notes)} unique notes values. Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
