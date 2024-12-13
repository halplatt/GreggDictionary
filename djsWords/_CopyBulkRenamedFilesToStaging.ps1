#Copy the renamed files to the !PNGStaging folder in the DJSWords folder
# Initialize a counter
$counter = 0

# Read the file _renamed_words.txt from the DJSWords _Bulkrename_words.csv
$lines = Get-Content -Path "_Bulkrename_words.txt"

# For each line in the file
foreach ($line in $lines) {
    # Split the line into two words
    $words = $line -split ","

    # Use the second word as the base name for the files
    $baseName = $words[1]

    # Define the file names
    $pngFile = $baseName + ".png"
    $txtFile = $baseName + ".txt"
    $tagPngFile = $baseName + ".tag.png"

    # Check if the files exist in the current directory and copy them to the !PNGStaging folder
    foreach ($file in $pngFile, $txtFile, $tagPngFile) {
        if (Test-Path -Path $file) {
            # Copy the file from the current directory to the !PNGStaging folder in the DJSWords folder
            Copy-Item -Path $file -Destination ".\!PNGStaging"
            # Increment the counter
            $counter++
        } else {
            Write-Output "File $file does not exist in the current directory."
        }
    }
}

# Print the counter
Write-Output "Number of files copied: $counter"

# Pause until user presses a key
Read-Host -Prompt "Press any key to exit . . ."