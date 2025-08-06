import json
import re

def process_json_file(input_file, output_file):
    """
    Process JSON file to extract content from parentheses in text field
    and move it to notes field with angle brackets.
    """
    
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process each object
    for item in data:
        if 'text' in item:
            text = item['text']
            notes = item.get('notes', '')
            
            # Find content in parentheses at the end of the text
            # This regex finds parentheses and their content at the end of the string
            match = re.search(r'\s*\(([^)]+)\)\s*$', text)
            
            if match:
                # Extract the content from parentheses
                parentheses_content = match.group(1)
                
                # Remove parentheses and trailing spaces from text
                new_text = re.sub(r'\s*\([^)]+\)\s*$', '', text)
                item['text'] = new_text
                
                # Add content to notes with angle brackets
                if notes.strip():  # If notes is not empty, add a space before
                    item['notes'] = notes + ' <' + parentheses_content + '>'
                else:
                    item['notes'] = '<' + parentheses_content + '>'
            
            # Ensure notes field exists even if empty
            if 'notes' not in item:
                item['notes'] = ''
    
    # Write the processed data back to the file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Processing complete. Output saved to {output_file}")
    
    # Show some examples of changes made
    print("\nExamples of changes made:")
    count = 0
    for item in data:
        if '<' in item.get('notes', '') and count < 5:
            print(f"Text: '{item['text']}' -> Notes: '{item['notes']}'")
            count += 1

if __name__ == "__main__":
    input_file = "!searchGSText.json"
    output_file = "!searchGSText.json"  # Overwrite the original file
    
    process_json_file(input_file, output_file)
    print("Script completed successfully!")
    import sys
    sys.exit(0)
