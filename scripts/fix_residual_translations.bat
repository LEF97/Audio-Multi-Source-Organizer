@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ==================================================
echo   AMSO — Réparation des résidus de traduction
echo ==================================================
echo.

.venv\Scripts\python.exe scripts\fix_residual_translations.py %*

echo.
echo Code de sortie : %ERRORLEVEL%
pause
