@echo off
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\publish_github_release.py %*
echo Code de sortie : %ERRORLEVEL%
pause
