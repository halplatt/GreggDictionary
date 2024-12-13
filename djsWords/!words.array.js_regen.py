import os
import json

# create _words.array.js file by getting the names of all .png files in the current directory
# (ie the /djsWords folder) that do not contain ".tag.png" in the name,
# and create a comma-delimited string of the file names and save as _words.array.js.  
# Note. This Python script runs in a second compared to the powershell version which takes about 1 minute
# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get all .png files in the script's directory that do not contain ".tag.png" in the name
files = [f for f in os.listdir(script_dir) if f.endswith('.png') and '.tag.png' not in f]

# Initialize an empty list to hold the file names
file_names = []

# Loop through the files and add their names (without the .png suffix) to the list
for file in files:
    file_name_without_extension = os.path.splitext(file)[0]
    # Add quotes around the file name
    file_names.append(f'"{file_name_without_extension}"')


# Join the file names with commas
comma_delimited_file_names = ','.join(file_names)

# Prefix the data with "var dict = [" and suffix it with "];"
comma_delimited_file_names = f'const dict = [{comma_delimited_file_names}];'

# Create the path for the output file
output_file_path = os.path.join(script_dir, '!words.array.js')

# Save the comma-delimited string to a file named _words.array.js in the script's directory
with open(output_file_path, 'w') as f:
    f.write(comma_delimited_file_names)