@echo off
REM ============================================
REM   Create Distribution Package
REM ============================================
title Create Distribution Package
color 0E
cls

echo.
echo ============================================
echo   Creating Distribution Package
echo ============================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Get version or use default
set VERSION=1.0
if "%1" neq "" set VERSION=%1

set PACKAGE_NAME=RC_Servo_Controller_v%VERSION%
set TEMP_DIR=%TEMP%\%PACKAGE_NAME%

echo [1/4] Creating temporary package directory...
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"
echo [OK] Created: %TEMP_DIR%
echo.

echo [2/4] Copying essential files...

REM Core application files (root level)
copy "main.py" "%TEMP_DIR%\" >nul 2>&1
copy "requirements.txt" "%TEMP_DIR%\" >nul 2>&1
copy "LAUNCH.bat" "%TEMP_DIR%\" >nul 2>&1
copy "SETUP.bat" "%TEMP_DIR%\" >nul 2>&1
if exist "README.md" copy "README.md" "%TEMP_DIR%\" >nul 2>&1

REM Create subdirectories in package
mkdir "%TEMP_DIR%\arduino" >nul 2>&1
mkdir "%TEMP_DIR%\docs" >nul 2>&1
mkdir "%TEMP_DIR%\scripts" >nul 2>&1

REM Arduino files
if exist "arduino\arduino_servo_control.ino" copy "arduino\arduino_servo_control.ino" "%TEMP_DIR%\arduino\" >nul 2>&1
if exist "arduino\arduino_servo_control_esp32s3.ino" copy "arduino\arduino_servo_control_esp32s3.ino" "%TEMP_DIR%\arduino\" >nul 2>&1
if exist "arduino\arduino_firmata_setup.ino" copy "arduino\arduino_firmata_setup.ino" "%TEMP_DIR%\arduino\" >nul 2>&1
if exist "arduino\ARDUINO_SETUP.md" copy "arduino\ARDUINO_SETUP.md" "%TEMP_DIR%\arduino\" >nul 2>&1
if exist "arduino\ESP32_S3_SETUP.md" copy "arduino\ESP32_S3_SETUP.md" "%TEMP_DIR%\arduino\" >nul 2>&1
if exist "arduino\POWER_TROUBLESHOOTING.md" copy "arduino\POWER_TROUBLESHOOTING.md" "%TEMP_DIR%\arduino\" >nul 2>&1

REM Documentation files
if exist "docs\QUICK_START.md" copy "docs\QUICK_START.md" "%TEMP_DIR%\docs\" >nul 2>&1
if exist "docs\PACKAGING.md" copy "docs\PACKAGING.md" "%TEMP_DIR%\docs\" >nul 2>&1
if exist "docs\PACKAGING_SUMMARY.md" copy "docs\PACKAGING_SUMMARY.md" "%TEMP_DIR%\docs\" >nul 2>&1
if exist "docs\DISTRIBUTION_README.txt" copy "docs\DISTRIBUTION_README.txt" "%TEMP_DIR%\docs\" >nul 2>&1
if exist "docs\ALTERNATIVE_METHODS.md" copy "docs\ALTERNATIVE_METHODS.md" "%TEMP_DIR%\docs\" >nul 2>&1
if exist "docs\AUTO_LAUNCH_SETUP.md" copy "docs\AUTO_LAUNCH_SETUP.md" "%TEMP_DIR%\docs\" >nul 2>&1
if exist "docs\FIX_COM_PORT.md" copy "docs\FIX_COM_PORT.md" "%TEMP_DIR%\docs\" >nul 2>&1

REM Supporting scripts (optional, but include for advanced users)
if exist "scripts\run.bat" copy "scripts\run.bat" "%TEMP_DIR%\scripts\" >nul 2>&1
if exist "scripts\servo_control_firmata.py" copy "scripts\servo_control_firmata.py" "%TEMP_DIR%\scripts\" >nul 2>&1

echo [OK] Files copied
echo.

echo [3/4] Creating ZIP archive...
set ZIP_FILE=%SCRIPT_DIR%%PACKAGE_NAME%.zip

REM Use PowerShell to create ZIP
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force" 2>nul

if exist "%ZIP_FILE%" (
    echo [OK] ZIP file created: %ZIP_FILE%
) else (
    echo [ERROR] Failed to create ZIP file
    echo.
    echo You can manually create a ZIP of the folder:
    echo   %TEMP_DIR%
    echo.
    pause
    exit /b 1
)

echo.

echo [4/4] Cleaning up...
rmdir /s /q "%TEMP_DIR%"
echo [OK] Cleanup complete
echo.

echo ============================================
echo   Package Created Successfully!
echo ============================================
echo.
echo Package location: %ZIP_FILE%
echo.
echo Package includes:
echo   - Main application (main.py)
echo   - Launcher scripts (LAUNCH.bat, SETUP.bat)
echo   - Documentation (README.md, docs/ folder)
echo   - Arduino firmware (arduino/ folder)
echo   - Supporting scripts (scripts/ folder)
echo   - Distribution instructions
echo.
echo The package maintains the organized folder structure for easy navigation.
echo.
echo You can now distribute this ZIP file to other users.
echo.
pause

