# Corrects a word in the file name in the current directory. 
# It prompts the user for the original word. 
# If user doesn't enter anything for the original word, the script exits.
# It prompts the user for the corrected word.
# If a file's name matched the original word, it is renamed to the corrected word instead.
# If any renaming occurs, the original and corrected words are logged in a file named '_renamed_words.txt'.
# '_renamed_words.txt' contains a list of original and corrected words separated by a comma.

while ($true) {
    # Prompt the user for the original word
    $originalWord = Read-Host -Prompt 'Enter the original word'
    # If the user doesn't enter anything, break the loop
    if (-not $originalWord) { break }

    # Prompt the user for the corrected word
    $correctWord = Read-Host -Prompt 'Enter the corrected word'
    write-output("Renaming files with prefix $originalWord to $correctWord")
    $renameOccurred = $false
    # Get all files in the current directory that start with the original word
    Get-ChildItem -Path '.' -Filter "$originalWord*" | 
    ForEach-Object {
        # Get the base name of the file without the extension
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
        # If the base name starts with the original word
        if ($baseName -match "^$originalWord(\.tag|)$") {
            # Replace the original word in the file name with the corrected word
            $newName = $_.Name -replace "^$originalWord", $correctWord
            # Rename the file
            Rename-Item -Path $_.FullName -NewName $newName
            Write-Output "Renamed $($_.Name) to $newName"
            # Remove the assignment statement for the unused variable 'renameOccurred'
            $renameOccurred = $true
        }
    }
    # If any renaming occurred, log the original and corrected words in '_renamed_words.txt'
    if ($renameOccurred) {
    Add-Content -Path '_renamed_words.txt' -Value "$originalWord,$correctWord"
    }
}