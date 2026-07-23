@echo off
setlocal
cd /d "%~dp0"
title Start Quote Image Generator Pro 1.7.0

echo ============================================
echo   Quote Image Generator Pro 1.7.0
echo ============================================
echo.
echo Starting from:
echo %CD%
echo.

call run_windows.bat
exit /b %errorlevel%
