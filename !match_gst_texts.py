from __future__ import annotations

import json
import re
from collections import defaultdict
from shutil import copy2
from pathlib import Path


BASE_DIR = Path(r"d:\HostGatorFiles\public_html\notes")
NOT_PATH = BASE_DIR / "notDictionary" / "!searchGSText.json"
DJS_PATH = BASE_DIR / "djsDictionary" / "!searchGSText.json"
OUTPUT_PATH = BASE_DIR / "!match_gst_texts(DJStoNot).txt"
DJS_WORDS_DIR = BASE_DIR / "djsWords"
NOT_WORDS_DIR = BASE_DIR / "notWords"


def load_entries(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_gst_for_match(gst: str) -> str:
    return re.sub(r"\d+", "", gst)


def collect_texts_by_gst(entries: list[dict[str, str]]) -> dict[str, list[str]]:
    texts_by_gst: dict[str, list[str]] = defaultdict(list)

    for entry in entries:
        gst = normalize_gst_for_match((entry.get("gst") or "").strip())
        text = (entry.get("text") or "").strip()

        if not gst or not text:
            continue

        texts_by_gst[gst].append(text)

    return dict(texts_by_gst)


def copy_matching_pngs() -> tuple[int, int, int, list[str]]:
    not_texts = collect_texts_by_gst(load_entries(NOT_PATH))
    djs_texts = collect_texts_by_gst(load_entries(DJS_PATH))

    copied = 0
    skipped_existing = 0
    missing_source = 0
    missing_examples: list[str] = []

    NOT_WORDS_DIR.mkdir(exist_ok=True)

    for gst in sorted(set(not_texts) & set(djs_texts)):
        source_text = sorted(set(djs_texts[gst]), key=str.casefold)[0]
        source_png = DJS_WORDS_DIR / f"{source_text}.png"

        if not source_png.exists():
            missing_source += len(set(not_texts[gst]))
            if len(missing_examples) < 20:
                missing_examples.append(f"{gst}: missing source {source_png.name}")
            continue

        for target_text in sorted(set(not_texts[gst]), key=str.casefold):
            target_png = NOT_WORDS_DIR / f"{target_text}.png"
            if target_png.exists():
                skipped_existing += 1
                continue

            copy2(source_png, target_png)
            copied += 1

    return copied, skipped_existing, missing_source, missing_examples


def build_report() -> str:
    not_texts = collect_texts_by_gst(load_entries(NOT_PATH))
    djs_texts = collect_texts_by_gst(load_entries(DJS_PATH))

    shared_gsts = sorted(set(not_texts) & set(djs_texts))
    lines: list[str] = [
        f"Shared non-empty gst values: {len(shared_gsts)}",
        f"Source A: {NOT_PATH}",
        f"Source B: {DJS_PATH}",
        "",
    ]

    for gst in shared_gsts:
        lines.append(f"GST: {gst}")
        lines.append("notDictionary text:")
        for text in sorted(set(not_texts[gst]), key=str.casefold):
            lines.append(f"- {text}")
        lines.append("djsDictionary text:")
        for text in sorted(set(djs_texts[gst]), key=str.casefold):
            lines.append(f"- {text}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    copied, skipped_existing, missing_source, missing_examples = copy_matching_pngs()

    lines = [
        f"Copied PNG files from {DJS_WORDS_DIR}: {copied}",
        f"Skipped existing targets already in {NOT_WORDS_DIR}: {skipped_existing}",
        f"Missing source copies from {DJS_WORDS_DIR}: {missing_source}",
    ]

    if missing_examples:
        lines.append("")
        lines.append("Missing source examples:")
        lines.extend(missing_examples)

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Copied {copied} PNG files into {NOT_WORDS_DIR}")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()