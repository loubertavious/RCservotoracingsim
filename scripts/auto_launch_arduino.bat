@echo off
REM Auto-launch script for Arduino RC Servo Racing Sim
REM This script monitors for Arduino connection and launches the program

REM Get the parent directory (project root)
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
cd /d "%PROJECT_ROOT%"

echo Waiting for Arduino to be connected...
echo Plug in your Arduino to start the program automatically.
echo.

:loop
REM Check for COM ports (Arduino typically uses COM3-COM20)
for /L %%i in (3,1,20) do (
    REM Try to check if port exists (basic check)
    mode COM%%i >nul 2>&1
    if not errorlevel 1 (
        REM Port exists, try to launch program
        echo Arduino detected on COM%%i! Launching program...
        python main.py
        exit /b
    )
)

REM Wait 2 seconds before checking again
timeout /t 2 /nobreak >nul
goto loop

