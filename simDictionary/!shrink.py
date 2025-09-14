import json

# Load the JSON data
with open('!reference.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Write the compressed JSON data back to the file
with open('!reference_compressed.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, separators=(',', ':'))

print("JSON file has been compressed.")