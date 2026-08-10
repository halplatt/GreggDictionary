#Change the name of the dictionary here
$dict = "dict2"
# Get all .png files in the /djsWords folder that do not contain ".tag.png" in the name
$files = Get-ChildItem $PSScriptRoot -Filter "*.png" | Where-Object { $_.Name -notlike "*.tag.png" }

# Initialize an empty array to hold the file names
$fileNames = @()

# Loop through the files and add their names (without the .png suffix) to the array
foreach ($file in $files) {
    $fileNameWithoutExtension = $file.BaseName
    $fileNames += "`"$fileNameWithoutExtension`""
}

# Join the file names with commas
$commaDelimitedFileNames = $fileNames -join ','

# Prefix the data with "var dict = [" and suffix it with "];"
$commaDelimitedFileNames = "const $dict = [" + $commaDelimitedFileNames + "];"

# Save the comma-delimited string to a file named words.json
Set-Content -Path "$PSScriptRoot\!words.array2.js" -Value $commaDelimitedFileNames