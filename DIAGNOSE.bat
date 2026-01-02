@echo off
REM ============================================
REM   Diagnostic Script - Troubleshooting
REM ============================================
title RC Servo Controller - Diagnostics
color 0E
cls

echo.
echo ============================================
echo   RC Servo Controller - Diagnostics
echo ============================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo [1/6] Checking current directory...
echo Current directory: %CD%
echo Script location: %SCRIPT_DIR%
echo.

echo [2/6] Checking for main.py...
if exist "main.py" (
    echo [OK] main.py found
) else (
    echo [ERROR] main.py NOT FOUND!
    echo This is the problem - main.py is missing.
    echo.
    echo Files in current directory:
    dir /b *.py 2>nul
    echo.
    pause
    exit /b 1
)
echo.

echo [3/6] Checking Python installation...
set PYTHON_CMD=
set PYTHON_FOUND=0

py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    set PYTHON_FOUND=1
    echo [OK] Found: py command
    py --version
    goto :python_check_done
)

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    echo [OK] Found: python command
    python --version
    goto :python_check_done
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    set PYTHON_FOUND=1
    echo [OK] Found: python3 command
    python3 --version
    goto :python_check_done
)

:python_check_done
if %PYTHON_FOUND%==0 (
    echo [ERROR] Python NOT FOUND!
    echo.
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo.

echo [4/6] Testing Python execution...
%PYTHON_CMD% -c "print('Python is working!')"
if errorlevel 1 (
    echo [ERROR] Python execution failed!
    echo.
    pause
    exit /b 1
)
echo [OK] Python can execute commands
echo.

echo [5/6] Checking dependencies...
%PYTHON_CMD% -c "import serial" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] pyserial not installed
    echo This is required - will try to install...
    %PYTHON_CMD% -m pip install pyserial
    if errorlevel 1 (
        echo [ERROR] Failed to install pyserial
    ) else (
        echo [OK] pyserial installed
    )
) else (
    echo [OK] pyserial is installed
)
echo.

echo [6/6] Testing main.py import...
echo Attempting to import main.py...
%PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); import main" 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to import main.py
    echo There may be a syntax error or missing dependency.
    echo.
    echo Check the error message above for details.
) else (
    echo [OK] main.py can be imported successfully
)
echo.

echo ============================================
echo   Diagnostic Complete
echo ============================================
echo.
echo If all checks passed, try running LAUNCH.bat again.
echo.
pause

