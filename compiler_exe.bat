@echo off
chcp 65001 >nul
setlocal

pushd "%~dp0"

echo ============================================================
echo   AMSO - Compilation de l'executable (.exe)
echo ============================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" scripts\build_exe.py %*

popd
echo.
pause
