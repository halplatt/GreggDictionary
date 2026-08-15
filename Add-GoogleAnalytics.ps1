# Inserts the GA4 gtag.js snippet into <head> of every .html file that doesn't already have it.
# Re-run safely; files already containing the Measurement ID are skipped.

$measurementId = "G-G2279BJEMY"
$snippet = @"
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=$measurementId"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '$measurementId');
</script>
"@

$root = $PSScriptRoot
$files = Get-ChildItem -Path $root -Recurse -Filter *.html -File

$updated = 0
foreach ($file in $files) {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    if ($content -match [regex]::Escape($measurementId)) {
        continue
    }
    if ($content -notmatch '(?i)<head[^>]*>') {
        Write-Warning "No <head> tag found, skipping: $($file.FullName)"
        continue
    }
    $newContent = [regex]::Replace($content, '(?i)(<head[^>]*>)', "`$1`r`n$snippet", 1)
    Set-Content -LiteralPath $file.FullName -Value $newContent -NoNewline
    $updated++
    Write-Host "Updated: $($file.FullName)"
}

Write-Host "`nDone. $updated file(s) updated out of $($files.Count) total .html files."
