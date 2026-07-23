@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Run run_windows.bat once before testing.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m unittest discover -s tests -v
pause
