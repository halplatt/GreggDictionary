# Corrects a word in the file name in the current directory.
# It reads a two-column list: original filename base, new filename base.
# Each matching file is renamed from "<original><ext>" to "<new><ext>".

$pairsPath = if (Test-Path -LiteralPath '_BulkRename_words.csv') {
    '_BulkRename_words.csv'
} elseif (Test-Path -LiteralPath '_BulkRename_words.txt') {
    '_BulkRename_words.txt'
} else {
    throw "Could not find _BulkRename_words.csv or _BulkRename_words.txt in the current folder."
}

$wordPairs = Import-Csv -Path $pairsPath -Header 'OriginalWord', 'CorrectWord'

$renamedCount = 0
$skippedCount = 0

foreach ($pair in $wordPairs) {
    $originalWord = ($pair.OriginalWord | ForEach-Object { $_.Trim() })
    $correctWord = ($pair.CorrectWord | ForEach-Object { $_.Trim() })

    if ([string]::IsNullOrWhiteSpace($originalWord) -or [string]::IsNullOrWhiteSpace($correctWord)) {
        $skippedCount++
        continue
    }

    # Match literal filename base only (no regex), preserving each file extension.
    $matches = Get-ChildItem -Path '.' -File | Where-Object {
        $_.BaseName -eq $originalWord
    }

    foreach ($file in $matches) {
        $newName = "$correctWord$($file.Extension)"

        if ($file.Name -eq $newName) {
            continue
        }

        if (Test-Path -LiteralPath (Join-Path $file.DirectoryName $newName)) {
            Write-Warning "Skipped (target exists): $($file.Name) -> $newName"
            $skippedCount++
            continue
        }

        Rename-Item -LiteralPath $file.FullName -NewName $newName
        Add-Content -LiteralPath '_renamed_words.txt' -Value "$originalWord,$correctWord"
        Write-Output "Renamed $($file.Name) to $newName"
        $renamedCount++
    }
}

Write-Output "Done. Renamed: $renamedCount, Skipped: $skippedCount"
