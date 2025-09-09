@echo off
REM Set code page to UTF-8
chcp 65001 >nul

echo GalHub - Build Script
echo ======================
echo.

REM Check Python environment
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python environment not found
    echo Please install Python 3.6 or higher
    echo.
    pause
    exit /b 1
)

echo Python environment found
echo.

REM Run Python build script
python build.py

if %errorlevel% equ 0 (
    echo.
    echo Build script completed successfully
) else (
    echo.
    echo Build script failed
)

echo.
pause