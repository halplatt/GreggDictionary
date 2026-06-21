# find_missing.ps1

$wordList   = "missing_words_ann.txt"
$sourceDir  = "out_dir"
$foundDir   = "found_dir"
$stillMissing = "still_missing.txt"

# Make sure the source list exists
if (-not (Test-Path $wordList)) {
    Write-Error "Word list not found: $wordList"
    exit 1
}

# Create the destination folder if it doesn't exist
if (-not (Test-Path $foundDir)) {
    New-Item -ItemType Directory -Path $foundDir | Out-Null
}

# Start with an empty "still missing" file (overwrite any previous run)
if (Test-Path $stillMissing) { Remove-Item $stillMissing }

$foundCount   = 0
$missingCount = 0

Get-Content $wordList | ForEach-Object {
    $word = $_.Trim()
    if ([string]::IsNullOrWhiteSpace($word)) { return }   # skip blank lines

    $sourceFile = Join-Path $sourceDir "$word.png"

    if (Test-Path $sourceFile) {
        Copy-Item $sourceFile -Destination $foundDir
        $foundCount++
    } else {
        Add-Content -Path $stillMissing -Value $word
        $missingCount++
    }
}

Write-Host "Done. Copied $foundCount file(s) to '$foundDir'."
Write-Host "$missingCount word(s) still missing, listed in '$stillMissing'."