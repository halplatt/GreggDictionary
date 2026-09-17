# Create a temporary directory
$TempDir = ".\tempfiles"
if (-not (Test-Path $TempDir)) {
    New-Item -ItemType Directory -Path $TempDir
}

# Array of CapCase file names
$files = @(
    "Aaron","Anacortes","Baraboo","Binghamton","Burke","Charlottesville","Comstock","Dawson",
    "East Aurora","Erie","Fort Worth","Grand Haven","Helen","Ira","Kalamazoo","Laurens",
    "Lucretia","Mayville","Monterey","Newfoundland","Oscar","Pittsfield","Rhinelander",
    "Salome","Sherman","Stuttgart","Turner","Wausau","Yonkers"
)

# Move all matching files (case-insensitive) to the temp directory
foreach ($name in $files) {
    $pattern = ($name -replace ' ', '[ _-]?') + ".png"
    $found = Get-ChildItem -Path . -Filter *.png | Where-Object { $_.Name -imatch "^$pattern$" }
    foreach ($file in $found) {
        Move-Item $file.FullName $TempDir
    }
}

Write-Host "Files moved to $TempDir. Now update your GitHub repository."