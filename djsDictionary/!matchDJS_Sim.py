import json
from pathlib import Path


def resolve_existing_file(base_dir: Path, candidates: list[str]) -> Path:
    for name in candidates:
        file_path = base_dir / name
        if file_path.exists():
            return file_path
    names = ", ".join(candidates)
    raise FileNotFoundError(f"Could not find any of: {names}")


def load_json_array(file_path: Path) -> list[dict]:
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected top-level JSON array in {file_path.name}")
    return data


def main() -> None:
    base_dir = Path(__file__).resolve().parent

    gst_text_path = resolve_existing_file(
        base_dir,
        ["!searchGSText.json"],
    )
    simplified_diff_path = resolve_existing_file(
        base_dir,
        ["!simplifiedDiff.json"],
    )

    gst_text_data = load_json_array(gst_text_path)
    simplified_diff_data = load_json_array(simplified_diff_path)

    notes_by_text = {}
    for item in simplified_diff_data:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        notes = item.get("notes")
        if isinstance(text, str) and isinstance(notes, str) and notes != "":
            notes_by_text[text] = notes

    updated_count = 0
    for item in gst_text_data:
        if not isinstance(item, dict):
            continue

        text = item.get("text")
        if not isinstance(text, str):
            continue

        replacement_gst = notes_by_text.get(text)
        if replacement_gst is None:
            continue

        current_gst = item.get("gst")
        if not isinstance(current_gst, str):
            current_gst = ""

        if current_gst != replacement_gst:
            item["gst"] = replacement_gst
            updated_count += 1

    with gst_text_path.open("w", encoding="utf-8") as f:
        json.dump(gst_text_data, f, indent=4)
        f.write("\n")

    print(f"Input A: {gst_text_path.name}")
    print(f"Input B: {simplified_diff_path.name}")
    print(f"Updated {updated_count} records in {gst_text_path.name}")


if __name__ == "__main__":
    main()
