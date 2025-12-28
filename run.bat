@echo off
echo RC Servo Racing Sim Controller
echo.

REM Try py launcher first (Windows), then python
set PYTHON_CMD=py
py --version >nul 2>&1
if errorlevel 1 (
    set PYTHON_CMD=python
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.7+ from https://www.python.org/
        pause
        exit /b 1
    )
)

echo Checking Python installation...
%PYTHON_CMD% --version

echo.
echo Checking dependencies...
%PYTHON_CMD% -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting application...
%PYTHON_CMD% main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application crashed. Check the error messages above.
    pause
)

