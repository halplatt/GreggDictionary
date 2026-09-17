#!/usr/bin/env python3
"""
convertYAGATS.py - Converts YAGATS JSON to GS format

This program converts a JSON file from YAGATS format to GS format by:
1. Reading the input JSON file (!searchYAGATSText.json)
2. Converting GST values to GST2 using the specified conversion chart
3. Collecting notes during conversion
4. Writing the output to a new JSON file (!searchGSText.json)
"""

import json
import re
from typing import Dict, List, Tuple

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
        's': ('s', 's1'),
        'z': ('s', 's2'),
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
        'x': ('x', 'x1'),
        'X': ('x', 'x2'),
        '5': ('ss', 's2-s1'),
        '3': ('ss', 's1-s2'),
        'y': ('ye', ''),
        ':': ('/', ''),
        '%': ('%', ''),
        '~': ('-', ''),
        '^': ('/', ''),
        '(': ('th', 'th1'),
        ')': ('th', 'th2'),
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

def convert_gst_to_gst2(gst: str, conversion_chart: Dict[str, Tuple[str, str]]) -> Tuple[str, str]:
    """
    Convert GST string to GST2 format using the conversion chart.
    Returns tuple (gst2, notes)
    """
    # First extract any parentheses content
    cleaned_gst, parentheses_notes = extract_parentheses_content(gst)
    
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
    """
    Convert the JSON file from YAGATS format to GS format.
    """
    conversion_chart = create_conversion_chart()
    
    try:
        # Read input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded {len(data)} entries from {input_file}")
        
        # Convert each entry
        converted_data = []
        for entry in data:
            if 'gst' in entry:
                gst2, notes = convert_gst_to_gst2(entry['gst'], conversion_chart)
                
                # Create new entry with existing fields plus GST2 and notes
                new_entry = entry.copy()
                new_entry['GST2'] = gst2
                new_entry['notes'] = notes
                
                converted_data.append(new_entry)
            else:
                # If no 'gst' field, add empty GST2 and notes
                new_entry = entry.copy()
                new_entry['GST2'] = ''
                new_entry['notes'] = ''
                converted_data.append(new_entry)
        
        # Write output JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, indent=4, ensure_ascii=False)
        
        print(f"Converted data written to {output_file}")
        print(f"Processed {len(converted_data)} entries")
        
        # Show some examples
        print("\nFirst 5 conversion examples:")
        for i, entry in enumerate(converted_data[:5]):
            if 'gst' in entry:
                print(f"  {i+1}. '{entry['gst']}' -> '{entry['GST2']}'")
                if entry['notes']:
                    print(f"      Notes: {entry['notes']}")
    
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file - {e}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function to run the conversion."""
    input_file = "!searchYAGATSText.json"
    output_file = "!searchGSText.json"
    
    print("YAGATS to GS Converter")
    print("=" * 30)
    
    convert_json_file(input_file, output_file)

if __name__ == "__main__":
    main()
