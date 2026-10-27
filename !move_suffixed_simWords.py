"""Move suffixed simWords files (e.g. avatar(1).png, avatar(x).txt) plus their
unsuffixed counterparts (avatar.png, avatar.txt) from ./simWords to ./simTemp.

Usage: python !move_suffixed_simWords.py [--dry-run]
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "simWords"
DEST = ROOT / "simTemp"
EXTS = {".png", ".txt"}
SUFFIX_RE = re.compile(r"^(?P<base>.+?)\((?P<tag>[^()]*)\)$")


def move(path, dry_run):
    target = DEST / path.name
    if target.exists():
        print(f"SKIP (exists in dest): {path.name}")
        return False
    print(f"{'WOULD MOVE' if dry_run else 'MOVE'}: {path.name}")
    if not dry_run:
        shutil.move(str(path), str(target))
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    if not SRC.is_dir():
        sys.exit(f"Missing folder: {SRC}")
    if not dry_run:
        DEST.mkdir(exist_ok=True)

    suffixed = [p for p in SRC.iterdir()
                if p.is_file() and p.suffix.lower() in EXTS and SUFFIX_RE.match(p.stem)]

    # Collect every file to move: the suffixed ones plus all unsuffixed siblings (png and txt).
    to_move = {p.name: p for p in suffixed}
    for p in suffixed:
        base = SUFFIX_RE.match(p.stem).group("base").rstrip()
        for ext in EXTS:
            sibling = SRC / f"{base}{ext}"
            if sibling.is_file():
                to_move[sibling.name] = sibling

    moved = sum(move(p, dry_run) for p in sorted(to_move.values()))
    print(f"\n{len(suffixed)} suffixed files found; {moved} files "
          f"{'would be moved' if dry_run else 'moved'} to {DEST}")


if __name__ == "__main__":
    main()
