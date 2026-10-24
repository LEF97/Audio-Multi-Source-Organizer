@echo off
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\check_file_sizes.py %*
echo Code de sortie : %ERRORLEVEL%
pause
