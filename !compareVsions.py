import json
import re


def normalize_gst(gst):
    """Remove numeric and prime labels used to distinguish GST variants."""
    return re.sub(r"[0-9'’′]", "", gst)

files = [
    r"D:\HostGatorFiles\public_html\notes\annDictionary\!searchGSText.json",
    r"D:\HostGatorFiles\public_html\notes\simDictionary\!searchGSText.json",
    r"D:\HostGatorFiles\public_html\notes\notDictionary\!searchGSText.json",
    r"D:\HostGatorFiles\public_html\notes\djsDictionary\!searchGSText.json"
]

sets = []
original_gst = {}

for filename in files:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Compare normalized GST values while retaining the original spelling.
    pairs = {
        (item["text"], normalize_gst(item["gst"]))
        for item in data
        if "text" in item and "gst" in item
    }

    if not original_gst:
        original_gst = {
            (item["text"], normalize_gst(item["gst"])): item["gst"]
            for item in data
            if "text" in item and "gst" in item
        }

    sets.append(pairs)

# Find pairs present in ALL four files
common = set.intersection(*sets)

# Sort by text, then gst
common = sorted(common, key=lambda x: (x[0].lower(), x[1]))

# Output CSV-style file
output_file = r"D:\HostGatorFiles\public_html\notes\!compareVersion.csv"

with open(output_file, "w", encoding="utf-8") as f:
    f.write("text,gst\n")
    for text, normalized_gst in common:
        gst = original_gst[(text, normalized_gst)]
        f.write(f'"{text}","{gst}"\n')

print(f"{len(common)} identical text,gst pairs found.")
print(f"Saved to: {output_file}")