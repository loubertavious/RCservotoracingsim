@echo off
REM ============================================
REM   RC Servo Racing Sim - Setup Script
REM ============================================
title RC Servo Racing Sim - Setup
color 0B
cls

echo.
echo ============================================
echo   RC Servo Racing Sim Controller
echo   Setup and Shortcut Creator
echo ============================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check Python installation
echo [1/4] Checking Python installation...
set PYTHON_CMD=
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :python_ok
)

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_ok
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_ok
)

echo [ERROR] Python is not installed or not in PATH
echo.
echo Please install Python 3.7 or higher from:
echo   https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation!
echo.
pause
exit /b 1

:python_ok
echo [OK] Python found:
%PYTHON_CMD% --version
echo.

REM Install core dependencies (required)
echo [2/4] Installing/updating dependencies...
echo This may take a few minutes...
echo.
%PYTHON_CMD% -m pip install --upgrade pip --quiet
echo Installing core dependencies (pyserial)...
%PYTHON_CMD% -m pip install pyserial
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install pyserial (required)
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
echo [OK] Core dependencies installed

REM Try to install pygame (optional)
echo.
echo Attempting to install pygame (optional - for real game controller support)...
echo Note: If pygame installation fails, the app will still work
echo       with the virtual on-screen wheel (no real controllers needed)
%PYTHON_CMD% -m pip install pygame --quiet 2>nul
if errorlevel 1 (
    echo [WARNING] pygame installation failed or skipped
    echo [INFO] The app will work with virtual controller only
    echo [INFO] Real game controllers will be disabled
    echo [INFO] This is normal on some systems - pygame is optional
) else (
    echo [OK] pygame installed successfully
)
echo.

REM Create desktop shortcut
echo [3/4] Creating desktop shortcut...
set SHORTCUT_NAME=RC Servo Controller.lnk
set TARGET_PATH=%SCRIPT_DIR%LAUNCH.bat
set ICON_PATH=%SystemRoot%\System32\shell32.dll,137

powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $desktop = [Environment]::GetFolderPath('Desktop'); $Shortcut = $WshShell.CreateShortcut(\"$desktop\$env:SHORTCUT_NAME\"); $Shortcut.TargetPath = '$TARGET_PATH'; $Shortcut.WorkingDirectory = '$SCRIPT_DIR'; $Shortcut.IconLocation = '$ICON_PATH'; $Shortcut.Description = 'RC Servo Racing Sim Controller'; $Shortcut.Save(); if (Test-Path \"$desktop\$env:SHORTCUT_NAME\") { Write-Host '[OK] Shortcut created successfully!' } else { Write-Host '[WARNING] Shortcut creation may have failed' }" 2>nul

if exist "%USERPROFILE%\Desktop\%SHORTCUT_NAME%" (
    echo [OK] Desktop shortcut created successfully!
) else (
    echo [WARNING] Could not create desktop shortcut automatically
    echo You can manually create a shortcut to LAUNCH.bat
)

echo.

REM Create Start Menu shortcut (optional)
echo [4/4] Creating Start Menu shortcut...
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
if not exist "%START_MENU%" mkdir "%START_MENU%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $startMenu = [Environment]::GetFolderPath('Programs'); $Shortcut = $WshShell.CreateShortcut(\"$startMenu\$env:SHORTCUT_NAME\"); $Shortcut.TargetPath = '$TARGET_PATH'; $Shortcut.WorkingDirectory = '$SCRIPT_DIR'; $Shortcut.IconLocation = '$ICON_PATH'; $Shortcut.Description = 'RC Servo Racing Sim Controller'; $Shortcut.Save(); if (Test-Path \"$startMenu\$env:SHORTCUT_NAME\") { Write-Host '[OK] Start Menu shortcut created!' } else { Write-Host '[INFO] Start Menu shortcut skipped' }" 2>nul

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo You can now launch the application by:
echo   1. Double-clicking "RC Servo Controller" on your Desktop
echo   2. Double-clicking "LAUNCH.bat" in this folder
echo   3. Using the Start Menu shortcut
echo.
echo To run the application, you need:
echo   - Python 3.7+ installed
echo   - Arduino connected via USB (optional, for servo control)
echo   - Game controller connected (optional, for input)
echo.
pause

