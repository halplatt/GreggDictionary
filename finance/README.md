# Portfolio CSV Upload Setup Guide

## What You Have Now:
- ✅ PowerShell script: `D:\HostGatorFiles\public_html\notes\finance\upload-portfolio.ps1`
- ✅ Configuration file: `D:\HostGatorFiles\public_html\notes\finance\ftp-config.json`
- ✅ Easy launcher: `D:\HostGatorFiles\public_html\notes\finance\UploadPortfolio.bat`
- ✅ Auto-delete launcher: `D:\HostGatorFiles\public_html\notes\finance\UploadAndDelete.bat`
- ✅ Backup launcher: `Documents\UploadPortfolio.bat`

## 🎯 **NEW FEATURE: File Selection**
The script now prompts you to select ANY CSV file and uploads it as `Portfolios.csv`!
- No need to rename files
- No need to move files to the finance folder
- Pick the most recent file from anywhere on your computer

## Quick Setup Steps:

### 1. Edit Your FTP Configuration
Open: `D:\HostGatorFiles\public_html\notes\finance\ftp-config.json`

Replace these values with your actual HostGator details:
```json
{
    "FtpUsername": "your-actual-ftp-username",
    "FtpPassword": "your-actual-ftp-password",
    "RemotePath": "/public_html/notes/finance/",
    "FtpServer": "your-actual-domain.com",
    "LocalFilePath": "C:\\path\\to\\your\\actual\\Portfolios.csv",
    "UsePassiveMode": true
}
```

### 2. Find Your HostGator FTP Info
Login to HostGator cPanel → File Manager → FTP Accounts
- **Server**: Usually your domain name
- **Username**: Your FTP username 
- **Port**: Usually 21 (standard FTP)

### 3. Daily Usage
**Option A**: Double-click `UploadPortfolio.bat` (in finance folder)
**Option B**: Double-click `UploadPortfolio.bat` (in Documents folder)
**Option C**: Run in PowerShell: `D:\HostGatorFiles\public_html\notes\finance\upload-portfolio.ps1`

## Features:
- 🔒 **Convenient**: Password stored in config file (no prompts)
- 📊 **Info Display**: Shows file size, date modified
- ✅ **Error Handling**: Clear success/failure messages
- 🎨 **Colorful Output**: Easy to read status updates
- ⚡ **Fast**: Direct FTP upload, no browser needed

## Troubleshooting:
- **"File not found"**: Update LocalFilePath in config.json
- **"Connection failed"**: Check FtpServer and FtpUsername
- **"Access denied"**: Verify FTP password and permissions
- **"Passive mode issues"**: Set UsePassiveMode to false

## Daily Workflow:

1. Generate your CSV file (anywhere on your computer)
2. Double-click `UploadPortfolio.bat` or `UploadAndDelete.bat`
3. **File dialog opens** - select your CSV file
4. Script uploads it as `Portfolios.csv` to HostGator
5. Choose whether to delete the source file (if using UploadPortfolio.bat)
6. Done! ✅

**Time saved**: ~2-3 minutes daily = ~10-15 hours per year!