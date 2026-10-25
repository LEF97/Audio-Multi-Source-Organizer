@echo off
cd /d "%~dp0.."
.venv\Scripts\python.exe scripts\audit_translations.py %*
echo.
echo Code de sortie : %ERRORLEVEL%
pause
