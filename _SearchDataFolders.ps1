# Define the folder path and the search string
$folder = "D:\\GitHub\\greggdict\\data\\"
#$folder = Join-Path -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition) -ChildPath "data"

while ($true) {
  $search = Read-Host -Prompt 'Enter the search string'
  # If the user doesn't enter anything, break the loop
  if (-not $search) { break }

  # Get all the csv files in the subfolders
  $files = Get-ChildItem -Path $folder -Filter _table.csv -Recurse

  # Loop through each file and search for the string
  foreach ($file in $files) {
    # Import the csv file as an array of strings
    $csv = Get-Content -Path $file.FullName
    
    # Find the lines that contain the search string
    $matches = $csv | Select-String -Pattern $search -SimpleMatch
    
    # If there are any matches, print the file name and the matching lines
    if ($matches) {
      Write-Output "File: $($file.FullName)"
      Write-Output $matches.Line
    }
  }
}