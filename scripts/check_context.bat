@echo off
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\check_context.py %*
echo Code de sortie : %ERRORLEVEL%
pause
