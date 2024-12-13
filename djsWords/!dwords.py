import os
import shutil

# Define the source directory and target directory
source_dir = './'
target_dir = './DWords'

# Create the target directory if it doesn't exist
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# Iterate over all files in the source directory
for filename in os.listdir(source_dir):
    # If the filename starts with 'D', copy it to the target directory
    if filename.startswith('D'):
        shutil.copy(os.path.join(source_dir, filename), target_dir)