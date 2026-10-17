@echo off
chcp 65001 > nul
echo ===================================================
echo     AUDIT QUALITÉ DE CODE - AMSO (Ruff + Mypy + Radon)
echo ===================================================
echo.

cd /d "%~dp0\.."

echo [1/4] Vérification de la syntaxe et des imports (Ruff)...
.venv\Scripts\ruff.exe check amso/
echo.

echo [2/4] Vérification statique des types (Mypy)...
.venv\Scripts\mypy.exe amso/
echo.

echo [3/4] Analyse de la complexité cyclomatique (Radon)...
.venv\Scripts\radon.exe cc amso/ -s -a -n C
echo.

echo [4/4] Exécution de la suite de tests et couverture...
.venv\Scripts\pytest.exe --cov=amso --cov-report=term-missing
echo.

echo ===================================================
echo     Audit terminé.
echo ===================================================
pause
