param(
    [string]$Folder = "D:\HostGatorFiles\public_html\notes\simTemp",
    [int]$Port = 8081
)

$toolFolder = Split-Path -Parent $PSCommandPath
$serverScript = Join-Path $toolFolder "!reviewpngs_server.py"
$reviewPage = "http://localhost:$Port/!reviewpngs.html"

if (-not (Test-Path -LiteralPath $Folder -PathType Container)) {
    throw "Review folder does not exist: $Folder"
}

if (-not (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)) {
    $pythonLauncher = (Get-Command py -ErrorAction Stop).Source
    $serverCommand = "& '$pythonLauncher' -u '$serverScript' --folder '$Folder' --port $Port --open-browser"
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $serverCommand) -WorkingDirectory $toolFolder
} else {
    Start-Process $reviewPage
}