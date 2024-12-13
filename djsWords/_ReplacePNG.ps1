# Define the directories
$stagingDir = "./!PNGstaging"
$replacedDir = "./!PNGreplaced"
$replacementDir = "./!PNGreplacement"
$addedDir = "./!PNGAdded"

# Get all files in the staging directory
$stagingFiles = Get-ChildItem -Path $stagingDir -File

# For each file in the staging directory
foreach ($file in $stagingFiles) {
    # Define the file paths
    $currentFile = "./" + $file.Name
    $replacedFile = $replacedDir + "/" + $file.Name
    $replacementFile = $replacementDir + "/" + $file.Name
    $addedFile = $addedDir + "/" + $file.Name
    $stagingFile = $stagingDir + "/" + $file.Name

    # Check if the file exists in the current directory and backup appropriately
    if (Test-Path -Path $currentFile) {
        # Move the file from the current directory to the replaced directory
        Move-Item -Path $currentFile -Destination $replacedFile
        # Copy the file from the staging directory to the replacement directory
        Copy-Item -Path $stagingFile -Destination $replacementFile
    } else {
         # Copy the file from the staging directory to the Added directory
        Copy-Item -Path $stagingFile -Destination $addedFile
    }
    
    # Move the file from the staging directory to the current directory
    Move-Item -Path $stagingFile -Destination "./"
}