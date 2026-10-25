@echo off
cd /d "%~dp0"
echo Démarrage d'AMSO en mode diagnostic visuel des traductions (⟦...⟧)...
.venv\Scripts\python.exe main.py --debug-i18n %*
echo Code de sortie : %ERRORLEVEL%
pause
