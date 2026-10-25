@echo off
cd /d "%~dp0.."
rem Sans argument : traduction complete (README, CHANGELOG, ROADMAP) par Ollama avec le modele par defaut.
rem Avec arguments : transmis tels quels (ex. --nav-only, --lang ja, --docs README).
if "%~1"=="" (
  echo Traduction par Ollama de README, CHANGELOG et ROADMAP...
  .venv\Scripts\python.exe scripts	ranslate_docs.py --ollama
) else (
  .venv\Scripts\python.exe scripts	ranslate_docs.py %*
)
echo Code de sortie : %ERRORLEVEL%
pause
