import json
import re
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

BASE = Path(__file__).resolve().parent
VERSIONS = ["ann", "djs", "pre", "sim", "not"]
# Versions whose words starting with "!" are skipped.
SKIP_BANG = {"ann": True, "djs": True, "pre": True, "sim": True, "not": True}


def read_text(path):
    try:
        return path.read_text(encoding="utf-8"), "utf-8"
    except UnicodeDecodeError as ex:
        raise RuntimeError(f"{path} is not valid UTF-8 ({ex}). Convert it to UTF-8 first.")


def load_words(path):
    text, _ = read_text(path)
    start, end = text.index("["), text.rindex("]")
    return json.loads(text[start:end + 1])


def run(version, dry_run, log):
    words_path = BASE / f"{version}Words" / "!words.array.js"
    json_path = BASE / f"{version}Dictionary" / "!searchGSText.json"
    bak_path = json_path.with_name(json_path.name + ".bak")

    words = load_words(words_path)
    json_text, enc = read_text(json_path)
    entries = json.loads(json_text)
    existing = {e["text"].lower() for e in entries}

    added = []
    for w in words:
        if SKIP_BANG[version] and w.startswith("!"):
            continue
        if w.lower() not in existing:
            existing.add(w.lower())
            added.append(w)
            entries.append({"text": w, "gst": "", "notes": ""})

    if dry_run:
        log(f"DRY RUN: no files changed ({version}).")
    else:
        shutil.copy2(json_path, bak_path)
        log(f"Backup written: {bak_path}")
        json_path.write_text(
            json.dumps(entries, indent=4, ensure_ascii=False) + "\n",
            encoding=enc,
        )
        log(f"Updated: {json_path}")

    log(f"Words in array: {len(words)}; words {'to add' if dry_run else 'added'}: {len(added)}")
    for w in added:
        log(f"  + {w}")


def main():
    root = tk.Tk()
    root.title("Update !searchGSText.json from words array")
    root.geometry("520x420")

    top = ttk.Frame(root, padding=8)
    top.pack(fill="x")
    ttk.Label(top, text="Version:").pack(side="left")
    version = tk.StringVar(value="sim")
    ttk.Combobox(top, textvariable=version, values=VERSIONS,
                 state="readonly", width=6).pack(side="left", padx=6)
    dry = tk.BooleanVar(value=False)
    ttk.Checkbutton(top, text="Dry run only", variable=dry).pack(side="left", padx=10)

    out = tk.Text(root, wrap="none")
    out.pack(fill="both", expand=True, padx=8, pady=8)

    def log(msg):
        out.insert("end", msg + "\n")
        out.see("end")
        root.update_idletasks()

    def start():
        out.delete("1.0", "end")
        try:
            run(version.get(), dry.get(), log)
        except Exception as ex:
            messagebox.showerror("Error", str(ex))
            log(f"ERROR: {ex}")

    ttk.Button(top, text="Start", command=start).pack(side="right")
    root.mainloop()


if __name__ == "__main__":
    main()
