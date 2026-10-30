@echo off
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\package_unix.py %*
echo Code de sortie : %ERRORLEVEL%
pause
