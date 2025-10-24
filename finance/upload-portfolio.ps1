# Enhanced PowerShell script to upload any CSV file as Portfolios.csv to HostGator
# Author: GitHub Copilot
# Usage: .\upload-portfolio.ps1

param(
    [string]$LocalFilePath = $null,
    [string]$ConfigFile = "D:\HostGatorFiles\public_html\notes\finance\ftp-config.json",
    [switch]$DeleteAfterUpload
)

# Function to create config file if it doesn't exist
function New-ConfigFile {
    param($ConfigPath)
    
    Write-Host "Setting up FTP configuration..." -ForegroundColor Yellow
    
    $config = @{
        LocalFilePath = "C:\path\to\your\csv\file.csv"
        FtpServer = "your-domain.com"
        FtpUsername = "your-ftp-username"
        FtpPassword = "your-ftp-password"
        RemotePath = "/public_html/notes/finance/"
        UsePassiveMode = $true
    }
    
    $config | ConvertTo-Json -Depth 3 | Out-File -FilePath $ConfigPath -Encoding UTF8
    
    Write-Host "Configuration file created at: $ConfigPath" -ForegroundColor Green
    Write-Host "Please edit this file with your actual FTP credentials before running again." -ForegroundColor Yellow
    Write-Host "Note: FTP password is stored in the config file for convenience." -ForegroundColor Cyan
    
    return $false
}

# Function to select a file using Windows file dialog
function Select-File {
    param(
        [string]$InitialDirectory = [Environment]::GetFolderPath('UserProfile') + '\Downloads',
        [string]$Filter = "CSV files (*.csv)|*.csv|All files (*.*)|*.*"
    )
    
    Add-Type -AssemblyName System.Windows.Forms
    
    $fileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $fileDialog.InitialDirectory = $InitialDirectory
    $fileDialog.Filter = $Filter
    $fileDialog.Title = "Select CSV file to upload as Portfolios.csv"
    $fileDialog.Multiselect = $false
    
    $result = $fileDialog.ShowDialog()
    
    if ($result -eq 'OK') {
        return $fileDialog.FileName
    }
    
    return $null
}

# Function to upload file via FTP
function Upload-FileToFTP {
    param($LocalFile, $Config, $Password)
    
    try {
        # Build FTP URI - always upload as Portfolios.csv regardless of source filename
        $targetFileName = "Portfolios.csv"
        $ftpUri = "ftp://$($Config.FtpServer)$($Config.RemotePath)$targetFileName"
        
        Write-Host "Connecting to: $($Config.FtpServer)" -ForegroundColor Cyan
        Write-Host "Username: $($Config.FtpUsername)" -ForegroundColor Cyan
        Write-Host "Uploading: $(Split-Path $LocalFile -Leaf) as $targetFileName" -ForegroundColor Cyan
        Write-Host "Remote path: $ftpUri" -ForegroundColor Cyan
        
        # Create FTP request
        $request = [System.Net.FtpWebRequest]::Create($ftpUri)
        $request.Credentials = New-Object System.Net.NetworkCredential($Config.FtpUsername, $Password)
        $request.Method = [System.Net.WebRequestMethods+Ftp]::UploadFile
        $request.UseBinary = $true
        $request.UsePassive = $Config.UsePassiveMode
        
        # Read file and upload
        $fileContent = [System.IO.File]::ReadAllBytes($LocalFile)
        $request.ContentLength = $fileContent.Length
        
        $requestStream = $request.GetRequestStream()
        $requestStream.Write($fileContent, 0, $fileContent.Length)
        $requestStream.Close()
        
        # Get response
        $response = $request.GetResponse()
        Write-Host "Upload successful! Status: $($response.StatusDescription)" -ForegroundColor Green
        $response.Close()
        
        return $true
    }
    catch {
        Write-Host "Error uploading file:" -ForegroundColor Red
        Write-Host "  Error Type: $($_.Exception.GetType().Name)" -ForegroundColor Red
        Write-Host "  Error Message: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.InnerException) {
            Write-Host "  Inner Exception: $($_.Exception.InnerException.Message)" -ForegroundColor Red
        }
        
        # Check for common FTP issues
        if ($_.Exception.Message -like "*530*") {
            Write-Host "  >>> This looks like a login authentication problem." -ForegroundColor Yellow
            Write-Host "  >>> Check your username and password in the config file." -ForegroundColor Yellow
        }
        elseif ($_.Exception.Message -like "*550*") {
            Write-Host "  >>> This looks like a file/directory permission problem." -ForegroundColor Yellow
            Write-Host "  >>> Check if the remote path exists and you have write permissions." -ForegroundColor Yellow
        }
        elseif ($_.Exception.Message -like "*timeout*" -or $_.Exception.Message -like "*unreachable*") {
            Write-Host "  >>> This looks like a connection problem." -ForegroundColor Yellow
            Write-Host "  >>> Check your FTP server address and internet connection." -ForegroundColor Yellow
        }
        
        return $false
    }
}

# Main script execution
Write-Host "=== Portfolio CSV Uploader ===" -ForegroundColor Magenta
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# Check if config file exists
if (-not (Test-Path $ConfigFile)) {
    if (-not (New-ConfigFile -ConfigPath $ConfigFile)) {
        exit 1
    }
}

# Load configuration
try {
    $config = Get-Content $ConfigFile | ConvertFrom-Json
    Write-Host "Configuration loaded successfully" -ForegroundColor Green
}
catch {
    Write-Host "Error reading config file: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Determine file path
if ($LocalFilePath) {
    $filePath = $LocalFilePath
    Write-Host "Using specified file: $filePath" -ForegroundColor Cyan
} else {
    # Show file selection dialog
    Write-Host "Select the CSV file to upload..." -ForegroundColor Yellow
    $filePath = Select-File
    
    if (-not $filePath) {
        Write-Host "File selection cancelled." -ForegroundColor Yellow
        Write-Host "`nPress any key to exit..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 0
    }
    
    Write-Host "Selected file: $filePath" -ForegroundColor Green
}

# Check if local file exists
if (-not (Test-Path $filePath)) {
    Write-Host "Selected file not found: $filePath" -ForegroundColor Red
    Write-Host "`nPress any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Get file info
$fileInfo = Get-Item $filePath
Write-Host "File: $($fileInfo.Name)" -ForegroundColor White
Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor White
Write-Host "Modified: $($fileInfo.LastWriteTime)" -ForegroundColor White

# Get password from config
$password = $config.FtpPassword

# Upload the file
Write-Host "`nStarting upload..." -ForegroundColor Yellow
$success = Upload-FileToFTP -LocalFile $filePath -Config $config -Password $password

# Clear password from memory
$password = $null

if ($success) {
    Write-Host "`n✅ Upload completed successfully!" -ForegroundColor Green
    Write-Host "Your file is now available as Portfolios.csv on HostGator." -ForegroundColor Green
    
    # Create local copy as Portfolios.csv in the finance directory
    try {
        $scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
        $localCopyPath = Join-Path $scriptDirectory "Portfolios.csv"
        
        # Only copy if it's not already the target file
        if ($filePath -ne $localCopyPath) {
            Copy-Item $filePath $localCopyPath -Force
            Write-Host "✅ Local copy saved as: $localCopyPath" -ForegroundColor Green
            Write-Host "You can now test locally with the same data that's on the webhost." -ForegroundColor Cyan
        } else {
            Write-Host "✅ File is already Portfolios.csv in the correct location." -ForegroundColor Green
        }
    }
    catch {
        Write-Host "⚠️ Warning: Failed to create local copy: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "Upload was successful, but local copy creation failed." -ForegroundColor Yellow
    }
    
    # Handle file deletion
    $shouldDelete = $false
    
    if ($DeleteAfterUpload) {
        $shouldDelete = $true
        Write-Host "Auto-deleting source file as requested..." -ForegroundColor Yellow
    } else {
        Write-Host "`nDo you want to delete the source file? (Y/N): " -ForegroundColor Yellow -NoNewline
        $deleteChoice = Read-Host
        $shouldDelete = ($deleteChoice -eq 'Y' -or $deleteChoice -eq 'y' -or $deleteChoice -eq 'yes' -or $deleteChoice -eq 'Yes')
    }
    
    if ($shouldDelete) {
        try {
            Remove-Item $filePath -Force
            Write-Host "✅ Source file deleted successfully!" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to delete source file: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "Source file kept as requested." -ForegroundColor Cyan
    }
} else {
    Write-Host "`n❌ Upload failed!" -ForegroundColor Red
}