@echo off
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\tnr_transitions.py %*
echo Code de sortie : %ERRORLEVEL%
pause
