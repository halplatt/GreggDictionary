# Check-MissingWords.ps1
# Reads 5000_word_index_expanded.txt and checks the annWords folder
# for a matching [word].png file. Missing words are saved to missing_words.txt.
#
# Folder structure:
#   [root]\Check-MissingWords.ps1
#   [root]\5000_word_index_expanded.txt
#   [root]\missing_words.txt          (output)
#   [root]\annWords\                  (folder containing .png files)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

$wordListFile  = Join-Path $scriptRoot "5000_word_index_expanded.txt"
$annWordsFolder = Join-Path $scriptRoot "djsWords"
$outputFile    = Join-Path $scriptRoot "missing_words_djs.txt"

# Verify the word list exists
if (-not (Test-Path $wordListFile)) {
    Write-Host "ERROR: Word list not found at $wordListFile" -ForegroundColor Red
    exit 1
}

# Verify the annWords folder exists
if (-not (Test-Path $annWordsFolder)) {
    Write-Host "ERROR: annWords folder not found at $annWordsFolder" -ForegroundColor Red
    exit 1
}

# Read all words from the file, skip blank lines
$words = Get-Content $wordListFile | Where-Object { $_.Trim() -ne "" }

$missingWords = @()
$foundCount = 0

foreach ($word in $words) {
    $word = $word.Trim()
    $pngFile = Join-Path $annWordsFolder "$word.png"

    if (Test-Path $pngFile) {
        $foundCount++
    } else {
        $missingWords += $word
    }
}

# Write missing words to output file
$missingWords | Set-Content $outputFile -Encoding UTF8

# Summary
$totalWords = $words.Count
$missingCount = $missingWords.Count

Write-Host ""
Write-Host "===== Results =====" -ForegroundColor Cyan
Write-Host "Total words checked:  $totalWords"
Write-Host "Found in ${annWordsFolder}:    $foundCount" -ForegroundColor Green
Write-Host "Missing from ${annWordsFolder}: $missingCount" -ForegroundColor Yellow
Write-Host ""
Write-Host "Missing words saved to: $outputFile"
