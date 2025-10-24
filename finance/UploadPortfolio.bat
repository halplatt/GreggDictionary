:: Portfolio CSV Upload Script
:: Uploads any selected CSV file to HostGator as Portfolios.csv and asks if you want to delete source file
@echo off
cd /d "D:\HostGatorFiles\public_html\notes\finance"
powershell.exe -ExecutionPolicy Bypass -File "D:\HostGatorFiles\public_html\notes\finance\upload-portfolio.ps1"