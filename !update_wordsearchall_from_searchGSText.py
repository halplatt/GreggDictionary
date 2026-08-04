import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable, List, Sequence, Set

FALLBACK_ENCODINGS: Sequence[str] = (
    "utf-8",
    "utf-8-sig",
    "cp1252",
    "latin-1",
)

SCRIPT_DIR = Path(__file__).resolve().parent


def resolve_path(path: str) -> Path:
    raw_path = Path(path)
    if raw_path.is_absolute():
        return raw_path

    candidates = [
        Path.cwd() / raw_path,
        SCRIPT_DIR / raw_path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return SCRIPT_DIR / raw_path


def read_text_with_fallback(path: str) -> str:
    resolved_path = resolve_path(path)
    last_err: Exception | None = None
    for enc in FALLBACK_ENCODINGS:
        try:
            with open(resolved_path, 'r', encoding=enc) as f:
                data = f.read()
            if enc != FALLBACK_ENCODINGS[0]:
                print(f"Note: decoded '{resolved_path}' using fallback encoding '{enc}'.")
            return data
        except UnicodeDecodeError as e:
            last_err = e
            continue
        except OSError as e:
            raise e
    raise last_err if last_err else RuntimeError(f"Failed to read {resolved_path}")


def load_json(path: str) -> Any:
    resolved_path = resolve_path(path)
    try:
        text = read_text_with_fallback(str(resolved_path))
    except OSError as e:
        print(f"Failed to read JSON '{resolved_path}': {e}", file=sys.stderr)
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON '{resolved_path}': {e}", file=sys.stderr)
        return None


def load_wordsearch_entries(path: str) -> List[dict]:
    resolved_path = resolve_path(path)
    if not resolved_path.exists():
        print(f"Wordsearch JSON not found: {resolved_path}", file=sys.stderr)
        return []
    with open(resolved_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Failed to parse wordsearch JSON '{resolved_path}': {e}", file=sys.stderr)
            return []
    if not isinstance(data, list):
        print(f"Wordsearch JSON root is not a list: {resolved_path}", file=sys.stderr)
        return []
    return data


def existing_lower_set(entries: List[dict]) -> Set[str]:
    values: Set[str] = set()
    for obj in entries:
        if isinstance(obj, dict):
            text = obj.get('text')
            if isinstance(text, str):
                normalized = text.strip()
                if normalized:
                    values.add(normalized.lower())
    return values


def extract_texts_from_search_gs(root: Any) -> Iterable[str]:
    if root is None:
        return

    if isinstance(root, list):
        for item in root:
            if not isinstance(item, dict):
                continue
            text = item.get('text')
            if isinstance(text, str):
                normalized = text.strip()
                if normalized:
                    yield normalized
        return

    if isinstance(root, dict):
        for key in ('items', 'entries', 'results', 'words'):
            if key in root:
                yield from extract_texts_from_search_gs(root[key])


def add_new_words(source_words: Iterable[str], wordsearch_entries: List[dict]) -> int:
    existing = existing_lower_set(wordsearch_entries)
    added = 0
    for word in source_words:
        lowered = word.lower()
        if lowered not in existing:
            wordsearch_entries.append({'text': word})
            existing.add(lowered)
            added += 1
    return added


def save_wordsearch(path: str, entries: List[dict], backup: bool):
    resolved_path = resolve_path(path)
    if backup and resolved_path.exists():
        backup_path = resolved_path.with_suffix(resolved_path.suffix + '.bak')
        try:
            if backup_path.exists():
                backup_path.unlink()
            os.replace(resolved_path, backup_path)
            print(f"Backup created: {backup_path}")
        except OSError as e:
            print(f"Warning: could not create backup: {e}", file=sys.stderr)
    with open(resolved_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser(
        description="Merge text entries from searchGSText JSON into a wordsearch JSON list"
    )
    ap.add_argument(
        '--source-file',
        default='notDictionary/!searchGSText.json',
        help='Path to the searchGSText JSON file',
    )
    ap.add_argument(
        '--json-file',
        default='!wordsearchall.json',
        help='Path to the wordsearch JSON list file to update',
    )
    ap.add_argument('--no-backup', action='store_true', help='Do not create .bak backup before writing')
    ap.add_argument('--dry-run', action='store_true', help='Report additions without writing changes')
    args = ap.parse_args()

    source_root = load_json(args.source_file)
    if source_root is None:
        return 1

    source_words = list(extract_texts_from_search_gs(source_root))
    print(f"Extracted {len(source_words)} candidate words from searchGSText JSON.")

    entries = load_wordsearch_entries(args.json_file)
    before = len(entries)
    added = add_new_words(source_words, entries)

    if args.dry_run:
        print(f"Dry run: would add {added} new words. New total would be {before + added}.")
        return 0

    save_wordsearch(args.json_file, entries, backup=not args.no_backup)
    print(f"Added {added} new words. Total entries: {len(entries)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())