@echo off
chcp 65001 >nul
setlocal

pushd "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" main.py %*

if errorlevel 1 (
    echo.
    echo [ERREUR] Une erreur est survenue lors de l'execution d'AMSO.
    pause
)

popd