# Corrects a word in the file name in the current directory. 
# It reads a CSV file where each line contains the original word and the corrected word.
# If a file's name matched the original word, it is renamed to the corrected word instead.
# If any renaming occurs, the original and corrected words are logged in a file named '_renamed_words.txt'.
# '_renamed_words.txt' contains a list of original and corrected words separated by a comma.

# Import the CSV file
$wordPairs = Import-Csv -Path '_BulkRename_words.txt' -Header 'OriginalWord', 'CorrectWord'

foreach ($pair in $wordPairs) {
    $originalWord = $pair.OriginalWord
    $correctWord = $pair.CorrectWord

    Write-Output("Renaming files with prefix $originalWord to $correctWord")
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
            $renameOccurred = $true
    	}
    }
    #If any renaming occurred, log the original and corrected words in '_renamed_words.txt'
    if ($renameOccurred) {
        Add-Content -Path '_renamed_words.txt' -Value "$originalWord,$correctWord"
    }
}
$x = Read-Host -Prompt 'press enter to exit'
