@echo off
REM ============================================
REM   RC Servo Racing Sim Controller Launcher
REM ============================================
title RC Servo Racing Sim Controller
color 0A

REM Prevent window from closing immediately on error
setlocal enabledelayedexpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Clear screen and show header
cls
echo.
echo ============================================
echo   RC Servo Racing Sim Controller
echo ============================================
echo.
echo Working directory: %CD%
echo.

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
echo.
echo ============================================
echo   ERROR: Python Not Found
echo ============================================
echo.
echo Python is not installed or not in PATH.
echo.
echo Please install Python 3.7 or higher from:
echo   https://www.python.org/downloads/
echo.
echo IMPORTANT: During installation, make sure to check:
echo   "Add Python to PATH"
echo.
echo After installing Python:
echo   1. Close this window
echo   2. Run SETUP.bat again
echo   3. Or run LAUNCH.bat again
echo.
echo Press any key to exit...
pause >nul
exit /b 1

:found_python
echo [OK] Python found:
%PYTHON_CMD% --version
echo.

REM Check if main.py exists
if not exist "main.py" (
    echo.
    echo ============================================
    echo   ERROR: main.py Not Found
    echo ============================================
    echo.
    echo main.py not found in current directory!
    echo.
    echo Current directory: %CD%
    echo.
    echo Please make sure you:
    echo   1. Extracted all files from the ZIP
    echo   2. Are running LAUNCH.bat from the correct folder
    echo   3. main.py is in the same folder as LAUNCH.bat
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Check and install dependencies
echo Checking dependencies...
%PYTHON_CMD% -c "import serial" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing required packages...
    echo This may take a few minutes on first run...
    echo.
    %PYTHON_CMD% -m pip install --upgrade pip --quiet
    %PYTHON_CMD% -m pip install pyserial
    if errorlevel 1 (
        echo.
        echo ============================================
        echo   ERROR: Failed to Install pyserial
        echo ============================================
        echo.
        echo pyserial is REQUIRED for this application.
        echo.
        echo Possible solutions:
        echo   1. Check your internet connection
        echo   2. Try running: pip install pyserial
        echo   3. Check if you have administrator rights
        echo   4. Try running SETUP.bat as administrator
        echo.
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
    echo [OK] Core dependencies installed
) else (
    echo [OK] Core dependencies already installed
)

REM Try to install pygame (optional - only needed for real game controllers)
echo.
echo Checking for pygame (optional - for real game controller support)...
%PYTHON_CMD% -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo [INFO] pygame not found - attempting to install...
    echo Note: If pygame installation fails, the app will still work
    echo       with the virtual on-screen wheel (no real controllers needed)
    echo.
    %PYTHON_CMD% -m pip install pygame --quiet 2>nul
    if errorlevel 1 (
        echo [WARNING] pygame installation failed or skipped
        echo [INFO] The app will work with virtual controller only
        echo [INFO] Real game controllers will be disabled
    ) else (
        echo [OK] pygame installed successfully
    )
) else (
    echo [OK] pygame already installed
)

echo.
echo ============================================
echo   Starting application...
echo ============================================
echo.

REM Test if Python can import main.py before running
echo Testing Python import...
%PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); import main" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to import main.py
    echo.
    echo This usually means:
    echo   - Syntax error in main.py
    echo   - Missing required dependency
    echo   - Python version incompatible
    echo.
    echo Running diagnostic test...
    %PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); import main" 2>&1
    echo.
    echo Please check the error message above.
    echo You can also run DIAGNOSE.bat for more detailed diagnostics.
    echo.
    pause
    exit /b 1
)

REM Run the application
echo [OK] Python import test passed
echo.
echo Launching application...
echo.

REM Run Python and capture both stdout and stderr
%PYTHON_CMD% main.py
set APP_EXIT_CODE=%ERRORLEVEL%

REM If Python crashed immediately, the exit code might be non-zero
if %APP_EXIT_CODE% neq 0 (
    REM Error occurred
) else (
    REM Check if Python actually ran (sometimes exits with 0 even on error)
    REM This is handled below
)

REM Check exit code
if %APP_EXIT_CODE% neq 0 (
    echo.
    echo ============================================
    echo   Application exited with an error
    echo ============================================
    echo.
    echo Exit code: %APP_EXIT_CODE%
    echo.
    echo Check the error messages above for details.
    echo.
    echo Common issues:
    echo   - Python version too old (need 3.7+)
    echo   - Missing dependencies (try running SETUP.bat)
    echo   - File permissions issue
    echo   - main.py has syntax errors
    echo.
) else (
    echo.
    echo Application closed normally.
    echo.
)

REM Always pause so user can see any messages
pause
exit /b %APP_EXIT_CODE%

