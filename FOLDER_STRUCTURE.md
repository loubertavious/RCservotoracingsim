# Repository Folder Structure

This document explains the organization of files in this repository.

## Root Level

Essential files that users interact with directly:

- `main.py` - Main application entry point
- `requirements.txt` - Python dependencies
- `README.md` - Main documentation
- `LAUNCH.bat` - Main launcher (double-click to run)
- `SETUP.bat` - Setup script (run once for initial setup)
- `CREATE_PACKAGE.bat` - Creates distribution ZIP file

## Subdirectories

### `/arduino/` - Arduino Firmware and Documentation

All Arduino-related files:

- `arduino_servo_control.ino` - Main Arduino firmware for standard boards
- `arduino_servo_control_esp32s3.ino` - ESP32-S3 specific firmware
- `arduino_firmata_setup.ino` - Alternative Firmata-based setup
- `ARDUINO_SETUP.md` - Arduino setup instructions
- `ESP32_S3_SETUP.md` - ESP32-S3 specific setup guide
- `POWER_TROUBLESHOOTING.md` - Power supply troubleshooting

### `/docs/` - Documentation

All documentation files:

- `QUICK_START.md` - Quick start guide
- `PACKAGING.md` - Advanced packaging guide
- `PACKAGING_SUMMARY.md` - Packaging solution overview
- `DISTRIBUTION_README.txt` - User instructions for distribution package
- `ALTERNATIVE_METHODS.md` - Alternative control methods
- `AUTO_LAUNCH_SETUP.md` - Auto-launch feature setup
- `FIX_COM_PORT.md` - COM port troubleshooting

### `/scripts/` - Supporting Scripts

Utility scripts for advanced users:

- `run.bat` - Legacy launcher (alternative to LAUNCH.bat)
- `launch_app.vbs` - Silent launcher (no console window)
- `create_shortcut.bat` - Creates desktop shortcut
- `auto_launch_arduino.bat` - Auto-launches when Arduino is connected
- `auto_launch_arduino.ps1` - PowerShell version of auto-launch
- `install_auto_launch.vbs` - Install auto-launch feature
- `servo_control_firmata.py` - Alternative Firmata-based control script

## File Organization Benefits

1. **Cleaner Root Directory**: Only essential files at root level
2. **Easy Navigation**: Related files grouped together
3. **Better for Distribution**: Organized structure in distribution packages
4. **Maintainability**: Easier to find and update files

## For Users

- **New users**: Just use `SETUP.bat` and `LAUNCH.bat` at the root
- **Arduino setup**: Check files in `/arduino/` folder
- **Documentation**: See files in `/docs/` folder
- **Advanced features**: Explore `/scripts/` folder

## For Developers

When adding new files:

- Arduino firmware → `/arduino/`
- Documentation → `/docs/`
- Utility scripts → `/scripts/`
- Core application files → Root level

