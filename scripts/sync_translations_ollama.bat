@echo off
setlocal

cd /d "%~dp0.."

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

set "MODEL=%~1"
if "%MODEL%"=="" (
    echo =======================================================
    echo   AMSO -- Traduction i18n via IA Locale (Ollama)
    echo =======================================================
    echo Modeles detectes : gemma4:latest, mistral:latest, qwen3.8:latest, deepseek-coder-v2:16b...
    set /p "MODEL=Modele a utiliser [defaut: gemma4:latest] : "
)

if "%MODEL%"=="" (
    set "MODEL=gemma4:latest"
)

echo.
echo Lancement de la synchronisation avec le modele : %MODEL%...
echo.

"%PYTHON_EXE%" scripts\sync_translations.py --ollama %MODEL%

echo.
echo Code de sortie : %ERRORLEVEL%
pause
