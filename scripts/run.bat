@echo off
title RC Servo Racing Sim Controller
color 0A

echo ========================================
echo   RC Servo Racing Sim Controller
echo ========================================
echo.

REM Get the parent directory (project root)
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

REM Try py launcher first (Windows), then python
set PYTHON_CMD=py
py --version >nul 2>&1
if errorlevel 1 (
    set PYTHON_CMD=python
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH
        echo.
        echo Please install Python 3.7+ from https://www.python.org/
        echo.
        pause
        exit /b 1
    )
)

echo [OK] Python found: 
%PYTHON_CMD% --version
echo.

echo Checking dependencies...
%PYTHON_CMD% -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required packages...
    %PYTHON_CMD% -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

echo.
echo ========================================
echo   Starting application...
echo ========================================
echo.

%PYTHON_CMD% main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed. Check the error messages above.
    echo.
    pause
)

