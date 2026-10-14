@echo off
chcp 65001 >nul
setlocal

pushd "%~dp0"

if exist "..\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=..\.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" sync_translations.py %*

popd
echo.
pause
