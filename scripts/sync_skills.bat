@echo off
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\sync_skills.py %*
echo Code de sortie : %ERRORLEVEL%
pause
