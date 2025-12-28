@echo off
echo Creating desktop shortcut...
echo.

set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=RC Servo Controller.lnk
set TARGET_PATH=%SCRIPT_DIR%launch_app.vbs
set ICON_PATH=%SystemRoot%\System32\shell32.dll,137

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%TARGET_PATH%'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.IconLocation = '%ICON_PATH%'; $Shortcut.Description = 'RC Servo Racing Sim Controller'; $Shortcut.Save()"

if exist "%USERPROFILE%\Desktop\%SHORTCUT_NAME%" (
    echo.
    echo ✓ Shortcut created successfully on Desktop!
    echo   Name: %SHORTCUT_NAME%
) else (
    echo.
    echo ✗ Failed to create shortcut. Trying alternative method...
    echo.
    echo You can manually create a shortcut:
    echo 1. Right-click on launch_app.vbs
    echo 2. Select "Create shortcut"
    echo 3. Move the shortcut to your Desktop
)

pause

