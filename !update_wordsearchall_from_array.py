import argparse
import json
import os
import re
import sys
from typing import List, Set, Sequence

# ---------------- Parsing Helpers ---------------- #
STRING_REGEX = re.compile(r"(['\"`])(.*?)\1")


FALLBACK_ENCODINGS: Sequence[str] = (
    "utf-8",
    "utf-8-sig",
    "cp1252",  # Common on Windows, handles 0x91/0x92 smart quotes
    "latin-1", # Last resort (lossless single-byte mapping)
)


def read_text_with_fallback(path: str, preferred: str | None = None) -> str:
    """Read a text file trying a sequence of encodings until one succeeds.

    preferred: if supplied, tried first before the default fallback list.
    Raises the last UnicodeDecodeError if all fail.
    """
    tried = []
    enc_list = []
    if preferred:
        enc_list.append(preferred)
    for enc in FALLBACK_ENCODINGS:
        if enc not in enc_list:
            enc_list.append(enc)
    last_err: Exception | None = None
    for enc in enc_list:
        try:
            with open(path, 'r', encoding=enc) as f:
                content = f.read()
            if enc != enc_list[0]:
                print(f"Note: decoded '{path}' using fallback encoding '{enc}'.")
            return content
        except (UnicodeDecodeError, OSError) as e:
            last_err = e
            tried.append(f"{enc}: {e.__class__.__name__}")
            continue
    if last_err:
        raise last_err
    raise RuntimeError(f"Failed to read file {path} for unknown reasons. Tried encodings: {tried}")


def extract_words_from_js(js_content: str) -> List[str]:
    """Attempt to extract a flat array of string literals from a JS file.

    This is intentionally forgiving: it looks for the first [...] block and
    extracts every quoted string inside, ignoring comments.
    """
    # Remove // and /* */ comments
    js_no_comments = re.sub(r"//.*", "", js_content)
    js_no_comments = re.sub(r"/\*.*?\*/", "", js_no_comments, flags=re.DOTALL)

    # Find first '[' and its matching ']' via a simple bracket balance
    start = js_no_comments.find('[')
    if start == -1:
        return []
    depth = 0
    end = None
    in_string = False
    string_char = ''
    escape = False
    for i, ch in enumerate(js_no_comments[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == string_char:
                in_string = False
        else:
            if ch in ('\"', "'", '`'):
                in_string = True
                string_char = ch
            elif ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    end = i
                    break
    if end is None:
        array_block = js_no_comments[start:]
    else:
        array_block = js_no_comments[start:end + 1]

    # Extract quoted substrings
    words = []
    for match in STRING_REGEX.finditer(array_block):
        value = match.group(2).strip()
        if value:
            words.append(value)
    return words


def load_json_entries(path: str) -> List[dict]:
    if not os.path.exists(path):
        print(f"JSON file not found: {path}", file=sys.stderr)
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON {path}: {e}", file=sys.stderr)
            return []
    if not isinstance(data, list):
        print(f"JSON root is not a list in {path}", file=sys.stderr)
        return []
    return data


def build_existing_set(entries: List[dict]) -> Set[str]:
    existing = set()
    for obj in entries:
        if isinstance(obj, dict):
            text = obj.get('text')
            if isinstance(text, str):
                existing.add(text.lower())
    return existing


def update_json(words: List[str], json_entries: List[dict]) -> int:
    existing = build_existing_set(json_entries)
    added = 0
    for w in words:
        lw = w.lower()
        if lw not in existing:
            json_entries.append({"text": w})
            existing.add(lw)
            added += 1
    return added


def save_json(path: str, data: List[dict], backup: bool):
    if backup and os.path.exists(path):
        bak_path = path + ".bak"
        try:
            if os.path.exists(bak_path):
                os.remove(bak_path)
            os.replace(path, bak_path)
            print(f"Backup created: {bak_path}")
        except OSError as e:
            print(f"Warning: could not create backup: {e}", file=sys.stderr)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')


def main():
    parser = argparse.ArgumentParser(description="Update !wordsearchall.json with words from !words.array.js")
    parser.add_argument('--words-file', default='preWords/!words.array.js', help='Path to JS file containing array of words')
    parser.add_argument('--json-file', default='!wordsearchall.json', help='Path to JSON file to update')
    parser.add_argument('--no-backup', action='store_true', help='Do not create .bak backup of JSON before writing')
    parser.add_argument('--dry-run', action='store_true', help='Parse and report but do not modify JSON file')
    args = parser.parse_args()

    # Load JS words
    try:
        js_content = read_text_with_fallback(args.words_file, preferred=None)
    except OSError as e:
        print(f"Failed to read words file: {e}", file=sys.stderr)
        return 1
    except UnicodeDecodeError as e:
        print(f"Could not decode words file with available fallbacks: {e}", file=sys.stderr)
        return 1

    words = extract_words_from_js(js_content)
    if not words:
        print("No words extracted from JS file (verify format).")

    # Load JSON
    entries = load_json_entries(args.json_file)

    before_count = len(entries)
    added = update_json(words, entries)

    if args.dry_run:
        print(f"Dry run: would add {added} new words. New total would be {before_count + added}.")
        return 0

    save_json(args.json_file, entries, backup=not args.no_backup)

    print(f"Added {added} new words. Total entries: {len(entries)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
