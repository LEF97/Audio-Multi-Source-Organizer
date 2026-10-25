@echo off
cd /d "%~dp0.."
echo =====================================================================
echo   AMSO — Traduction et synchronisation des 43 langues via Ollama
echo =====================================================================
.venv\Scripts\python.exe scripts\sync_translations.py --ollama gemma4:latest %*
echo.
echo Code de sortie : %ERRORLEVEL%
pause
