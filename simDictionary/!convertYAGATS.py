#!/usr/bin/env python3
"""convertYAGATS.py - Convert YAGATS JSON to GS format

Usage:
    python !convertYAGATS.py [-i INPUT] [-o OUTPUT] [--no-examples]

Default input file: !searchYAGATSText.json (resolver will also try without '!')
Default output file: !searchGSText.json

Process:
1. Load input JSON list of entries containing 'YAGATS' field(s)
2. Convert each 'YAGATS' value to GS 'gst' using conversion chart rules
3. Extract any parenthetical notes and append as dash-separated notes
4. Write enriched entries (adding 'gst' and 'notes') to output JSON (overwriting existing 'gst' if present)

If the exact input name is not found the script attempts helpful fallbacks
and informs which resolved file is used. Examples of first 5 conversions are
printed unless suppressed with --no-examples.
"""

import json
import re
import os
import glob
import argparse
from typing import Dict, List, Tuple, Optional

def create_conversion_chart() -> Dict[str, Tuple[str, str]]:
    """
    Creates the conversion chart mapping YAGATS characters to GS format.
    Returns dict where key is YAGATS char and value is tuple (gs_char, note)
    """
    return {
        'e': ('e', ''),
        'i': ('i', ''),
        'o': ('o', ''),
        'u': ('u', ''),
        's': ('s1', ''),
        'z': ('s2', ''),
        'f': ('f', ''),
        'v': ('v', ''),
        'p': ('p', ''),
        'b': ('b', ''),
        'm': ('m', ''),
        'n': ('n', ''),
        'k': ('k', ''),
        'g': ('g', ''),
        'r': ('r', ''),
        'l': ('l', ''),
        't': ('t', ''),
        'd': ('d', ''),
        'c': ('ch', ''),
        'j': ('j', ''),
        'h': ('h', ''),
        'q': ('h', ''),
        '@': ('h', ''),
        'A': ('h', ''),
        'w': ('w', ''),
        'x': ('x1', ''),
        'X': ('x2', ''),
        '5': ('s2-s1', ''),
        '3': ('s1-s2', ''),
        'y': ('ye', ''),
        ':': ('/', ''),
        '%': ('%', ''),
        '~': ('-', ''),
        '^': ('/', ''),
        '(': ('th1', ''),
        ')': ('th2', ''),
        '$': ('sh', ''),
        # Multi-character patterns
        'au': ('a-u', ''),
        'ea': ('ea', ''),
        'eu': ('e-u', ''),
        'io': ('io', ''),
        'oe': ('o-e', ''),
        'ya': ('ya', ''),
        'ye': ('ye', ''),
        'NT': ('nt', ''),
        'TN': ('tn', ''),
        'MD': ('md', ''),
        'DM': ('tm', ''),
        'MN': ('mn', ''),
        'TD': ('td', ''),
        'NG': ('ng', ''),
        'NK': ('nk', ''),
        'LD': ('ld', ''),
        'RD': ('rd', ''),
        'DV': ('tf', ''),
        'JD': ('jnt', ''),
        'PT': ('jnt', ''),
    }

def extract_parentheses_content(text: str) -> Tuple[str, List[str]]:
    """
    Extract content within parentheses and return cleaned text and extracted notes.
    """
    notes = []
    # Find all content within parentheses
    parentheses_pattern = r'\([^)]*\)'
    matches = re.findall(parentheses_pattern, text)
    
    # Extract the content without parentheses
    for match in matches:
        notes.append(match[1:-1])  # Remove the parentheses
    
    # Remove parentheses content from text
    cleaned_text = re.sub(parentheses_pattern, '', text)
    
    return cleaned_text, notes

def convert_YAGATS_to_gst(yagats: str, conversion_chart: Dict[str, Tuple[str, str]]) -> Tuple[str, str]:
    """Convert a YAGATS string to GS gst format.

    Returns (gst, notes).
    """
    # First extract any parentheses content
    cleaned_gst, parentheses_notes = extract_parentheses_content(yagats)
    
    # Initialize result and notes
    result_parts = []
    conversion_notes = []
    
    # Add parentheses notes to conversion notes
    conversion_notes.extend(parentheses_notes)
    
    i = 0
    while i < len(cleaned_gst):
        matched = False
        
        # Try to match multi-character patterns first (longest first)
        for pattern_length in [3, 2]:  # Check 3-char then 2-char patterns
            if i + pattern_length <= len(cleaned_gst):
                pattern = cleaned_gst[i:i + pattern_length]
                if pattern in conversion_chart:
                    conversion, note = conversion_chart[pattern]
                    if conversion in [':', '^']:  # Special handling for : and ^
                        result_parts.append('/')
                    else:
                        result_parts.append(conversion)
                    if note:
                        conversion_notes.append(note)
                    i += pattern_length
                    matched = True
                    break
        
        # If no multi-character pattern matched, try single character
        if not matched and i < len(cleaned_gst):
            char = cleaned_gst[i]
            if char in conversion_chart:
                conversion, note = conversion_chart[char]
                if conversion in [':', '^']:  # Special handling for : and ^
                    result_parts.append('/')
                else:
                    result_parts.append(conversion)
                if note:
                    conversion_notes.append(note)
            else:
                # If character not in conversion chart, keep as is
                result_parts.append(char)
            i += 1
    
    # Join result parts with '-' except for '/' characters
    gst2_parts = []
    for part in result_parts:
        if part == '/':
            gst2_parts.append(part)
        else:
            gst2_parts.append(part)
    
    # Join with '-' but handle '/' specially
    gst2 = ''
    for i, part in enumerate(gst2_parts):
        if i == 0:
            gst2 = part
        elif part == '/' or gst2_parts[i-1] == '/':
            gst2 += part
        else:
            gst2 += '-' + part
    
    # Join notes
    notes_str = '-'.join(conversion_notes) if conversion_notes else ''
    
    return gst2, notes_str

def convert_json_file(input_file: str, output_file: str):
    """Convert JSON file reading 'YAGATS' field to produce 'gst' and 'notes'."""
    conversion_chart = create_conversion_chart()
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file - {e}")
        return

    print(f"Loaded {len(data)} entries from {input_file}")
    converted_data = []
    for entry in data:
        if 'YAGATS' in entry:
            gst_val, notes = convert_YAGATS_to_gst(entry['YAGATS'], conversion_chart)
            new_entry = entry.copy()
            new_entry['gst'] = gst_val
            new_entry['notes'] = notes
            converted_data.append(new_entry)
        else:
            new_entry = entry.copy()
            if 'gst' not in new_entry:
                new_entry['gst'] = ''
            new_entry['notes'] = new_entry.get('notes', '')
            converted_data.append(new_entry)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing output file '{output_file}': {e}")
        return

    print(f"Converted data written to {output_file}")
    print(f"Processed {len(converted_data)} entries")
    print("\nFirst 5 conversion examples:")
    for i, entry in enumerate(converted_data[:5]):
        if 'YAGATS' in entry:
            print(f"  {i+1}. '{entry['YAGATS']}' -> '{entry['gst']}'")
            if entry.get('notes'):
                print(f"      Notes: {entry['notes']}")

def resolve_input_file(candidate: str) -> Optional[str]:
    """Resolve the input filename with a few helpful fallbacks.

    Order tried:
    1. As provided
    2. If starts with '!' and not found, try without '!'
    3. If still not found, glob for *searchYAGATSText*.json variants
    Returns the path if found else None.
    """
    if os.path.isfile(candidate):
        return candidate
    # Try removing leading '!'
    if candidate.startswith('!'):
        alt = candidate[1:]
        if os.path.isfile(alt):
            return alt
    # Try glob suggestions
    stem = candidate.replace('!', '').replace('.json', '')
    patterns = [f"*{stem}*.json", f"*{stem}*Text*.json"]
    matches = []
    for pattern in patterns:
        matches.extend(glob.glob(pattern))
    # Deduplicate preserving order
    seen = set()
    unique_matches = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            unique_matches.append(m)
    if unique_matches:
        # Pick the first as best guess
        return unique_matches[0]
    return None


def main():
    """Main function to run the conversion with CLI support."""
    parser = argparse.ArgumentParser(description="Convert YAGATS JSON to GS format")
    parser.add_argument('-i', '--input', default='!searchYAGATSText.json', help='Input YAGATS JSON file (default: !searchYAGATSText.json)')
    parser.add_argument('-o', '--output', default='!searchGSText.json', help='Output GS JSON file (default: !searchGSText.json)')
    parser.add_argument('--no-examples', action='store_true', help='Suppress example output lines')
    args = parser.parse_args()

    print("YAGATS to GS Converter")
    print("=" * 30)

    resolved_input = resolve_input_file(args.input)
    if not resolved_input:
        print(f"Error: Input file '{args.input}' not found and no close matches located.")
        return
    if resolved_input != args.input:
        print(f"Using resolved input file: {resolved_input}")

    conversion_chart = create_conversion_chart()
    try:
        with open(resolved_input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{resolved_input}' not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file - {e}")
        return

    print(f"Loaded {len(data)} entries from {resolved_input}")
    converted_data = []
    for entry in data:
        if 'YAGATS' in entry:
            gst_val, notes = convert_YAGATS_to_gst(entry['YAGATS'], conversion_chart)
            new_entry = entry.copy()
            new_entry['gst'] = gst_val
            new_entry['notes'] = notes
            converted_data.append(new_entry)
        else:
            new_entry = entry.copy()
            if 'gst' not in new_entry:
                new_entry['gst'] = ''
            new_entry['notes'] = new_entry.get('notes', '')
            converted_data.append(new_entry)

    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing output file '{args.output}': {e}")
        return

    print(f"Converted data written to {args.output}")
    print(f"Processed {len(converted_data)} entries")

    if not args.no_examples:
        print("\nFirst 5 conversion examples:")
        for i, entry in enumerate(converted_data[:5]):
            if 'YAGATS' in entry:
                print(f"  {i+1}. '{entry['YAGATS']}' -> '{entry['gst']}'")
                if entry.get('notes'):
                    print(f"      Notes: {entry['notes']}")

if __name__ == "__main__":
    main()
