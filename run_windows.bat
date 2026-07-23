@echo off
setlocal
cd /d "%~dp0"
title Quote Image Generator Pro 1.7.0

findstr /C:"1.7.0" app.py >nul
if errorlevel 1 (
    echo ERROR: This folder does not contain Version 1.7.0.
    echo You are opening an older copy of the application.
    echo Extract the new ZIP into a NEW folder and run START_HERE_v1.7.0.bat.
    pause
    exit /b 1
)

echo Current folder: %CD%
echo Confirmed version: 1.7.0
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo Python was not found.
    echo Install Python 3.11 or newer from https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 goto :error
)

echo Installing or checking required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Starting Quote Image Generator Pro...
".venv\Scripts\python.exe" app.py
if errorlevel 1 goto :runtime_error
exit /b 0

:runtime_error
echo.
echo The application stopped because of the error shown above.
echo Please take a screenshot of the full error and send it for support.
pause
exit /b 1

:error
echo.
echo Installation failed. Check your internet connection and Python installation.
pause
exit /b 1
