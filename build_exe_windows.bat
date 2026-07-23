@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Run run_windows.bat once before building the EXE.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install pyinstaller
if errorlevel 1 goto :error

".venv\Scripts\pyinstaller.exe" ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name "QuoteImageGeneratorPro" ^
    --icon "assets\QuoteImageGeneratorPro.ico" ^
    --add-data "assets\QuoteImageGeneratorPro.ico;assets" ^
    --collect-all PIL ^
    app.py

if errorlevel 1 goto :error
echo.
echo EXE created successfully:
echo %CD%\dist\QuoteImageGeneratorPro.exe
pause
exit /b 0

:error
echo EXE build failed.
pause
exit /b 1
