@echo off
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\verify.py %*
echo Code de sortie : %ERRORLEVEL%
pause
