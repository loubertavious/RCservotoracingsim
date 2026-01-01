@echo off
REM ============================================
REM   RC Servo Racing Sim Controller Launcher
REM ============================================
title RC Servo Racing Sim Controller
color 0A
cls

echo.
echo ============================================
echo   RC Servo Racing Sim Controller
echo ============================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Try py launcher first (Windows), then python, then python3
set PYTHON_CMD=
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :found_python
)

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :found_python
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :found_python
)

:not_found
echo [ERROR] Python is not installed or not in PATH
echo.
echo Please install Python 3.7 or higher from:
echo   https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation!
echo.
pause
exit /b 1

:found_python
echo [OK] Python found:
%PYTHON_CMD% --version
echo.

REM Check if main.py exists
if not exist "main.py" (
    echo [ERROR] main.py not found in current directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Check and install dependencies
echo Checking dependencies...
%PYTHON_CMD% -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required packages...
    echo This may take a few minutes on first run...
    echo.
    %PYTHON_CMD% -m pip install --upgrade pip --quiet
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies
        echo Please check your internet connection and try again.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed successfully
) else (
    echo [OK] Dependencies already installed
)

echo.
echo ============================================
echo   Starting application...
echo ============================================
echo.

REM Run the application
%PYTHON_CMD% main.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ============================================
    echo   Application exited with an error
    echo ============================================
    echo.
    echo Check the error messages above for details.
    echo.
    pause
)

exit /b 0

