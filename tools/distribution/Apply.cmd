@echo off
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Patch-Apathy-Kiwame.ps1" %*
if errorlevel 1 (echo Patch stopped. Read the message above. & pause & exit /b 1)
pause
