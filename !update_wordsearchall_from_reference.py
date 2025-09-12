import argparse
import json
import os
import sys
from typing import List, Set, Sequence, Iterable, Any

FALLBACK_ENCODINGS: Sequence[str] = (
    "utf-8",
    "utf-8-sig",
    "cp1252",
    "latin-1",
)


def read_text_with_fallback(path: str) -> str:
    last_err: Exception | None = None
    for enc in FALLBACK_ENCODINGS:
        try:
            with open(path, 'r', encoding=enc) as f:
                data = f.read()
            if enc != FALLBACK_ENCODINGS[0]:
                print(f"Note: decoded '{path}' using fallback encoding '{enc}'.")
            return data
        except UnicodeDecodeError as e:
            last_err = e
            continue
        except OSError as e:
            raise e
    raise last_err if last_err else RuntimeError(f"Failed to read {path}")


def load_json(path: str) -> Any:
    text = read_text_with_fallback(path)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON '{path}': {e}", file=sys.stderr)
        return None


def load_wordsearch_entries(path: str) -> List[dict]:
    if not os.path.exists(path):
        print(f"Wordsearch JSON not found: {path}", file=sys.stderr)
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Failed to parse wordsearch JSON '{path}': {e}", file=sys.stderr)
            return []
    if not isinstance(data, list):
        print(f"Wordsearch JSON root is not a list: {path}", file=sys.stderr)
        return []
    return data


def existing_lower_set(entries: List[dict]) -> Set[str]:
    s: Set[str] = set()
    for obj in entries:
        if isinstance(obj, dict):
            val = obj.get('text')
            if isinstance(val, str):
                s.add(val.lower())
    return s


def extract_words_from_reference(root: Any) -> Iterable[str]:
    """Yield each word.t (and variants) found in the reference structure.

    Expected patterns (robust):
      - root is list of pages, each page dict may have key 'word' (dict or list) containing objects with 't'.
      - page may also contain 'words' (list) similar structure.
      - root may be an object with key 'pages'.
    """
    if root is None:
        return

    # If root has 'pages'
    if isinstance(root, dict) and 'pages' in root and isinstance(root['pages'], list):
        for page in root['pages']:
            yield from extract_words_from_reference(page)
        return

    # If root is a list treat elements as pages
    if isinstance(root, list):
        for item in root:
            yield from extract_words_from_reference(item)
        return

    if not isinstance(root, dict):
        return

    def from_word_container(container):
        if isinstance(container, dict):
            t = container.get('t')
            if isinstance(t, str) and t.strip():
                yield t.strip()
        elif isinstance(container, list):
            for sub in container:
                if isinstance(sub, dict):
                    t = sub.get('t')
                    if isinstance(t, str) and t.strip():
                        yield t.strip()

    if 'word' in root:
        yield from from_word_container(root['word'])
    if 'words' in root:
        yield from from_word_container(root['words'])


def add_new_words(ref_words: Iterable[str], wordsearch_entries: List[dict]) -> int:
    existing = existing_lower_set(wordsearch_entries)
    added = 0
    for w in ref_words:
        lw = w.lower()
        if lw not in existing:
            wordsearch_entries.append({'text': w})
            existing.add(lw)
            added += 1
    return added


def save_wordsearch(path: str, entries: List[dict], backup: bool):
    if backup and os.path.exists(path):
        bak = path + '.bak'
        try:
            if os.path.exists(bak):
                os.remove(bak)
            os.replace(path, bak)
            print(f"Backup created: {bak}")
        except OSError as e:
            print(f"Warning: could not create backup: {e}", file=sys.stderr)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser(description="Merge page.word.t entries from reference into !wordsearchall.json")
    ap.add_argument('--ref-file', default='simDictionary/!reference.json', help='Path to reference JSON file')
    ap.add_argument('--json-file', default='!wordsearchall.json', help='Path to wordsearch JSON list file')
    ap.add_argument('--no-backup', action='store_true', help='Do not create .bak backup before writing')
    ap.add_argument('--dry-run', action='store_true', help='Report additions without writing changes')
    args = ap.parse_args()

    ref_root = load_json(args.ref_file)
    if ref_root is None:
        return 1

    ref_words = list(extract_words_from_reference(ref_root))
    print(f"Extracted {len(ref_words)} candidate words from reference.")

    entries = load_wordsearch_entries(args.json_file)
    before = len(entries)

    added = add_new_words(ref_words, entries)

    if args.dry_run:
        print(f"Dry run: would add {added} new words. New total would be {before + added}.")
        return 0

    save_wordsearch(args.json_file, entries, backup=not args.no_backup)
    print(f"Added {added} new words. Total entries: {len(entries)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
