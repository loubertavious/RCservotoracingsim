================================================================================
  RC SERVO RACING SIM CONTROLLER - DISTRIBUTION PACKAGE
================================================================================

INSTALLATION INSTRUCTIONS
=========================

1. EXTRACT THE ZIP FILE
   - Extract all files to any folder (e.g., Desktop or Documents)
   - Keep all files together in the same folder

2. RUN SETUP (First Time Only)
   - Double-click "SETUP.bat"
   - This will:
     * Check if Python is installed
     * Install required dependencies
     * Create desktop shortcut

3. LAUNCH THE APPLICATION
   - Double-click "RC Servo Controller" on your Desktop, OR
   - Double-click "LAUNCH.bat" in the program folder

REQUIREMENTS
============

- Windows 10 or later
- Python 3.7 or higher (download from https://www.python.org/downloads/)
  * During installation, make sure to check "Add Python to PATH"
- Internet connection (for first-time dependency installation)

WHAT'S INCLUDED
===============

- main.py                    - Main application
- LAUNCH.bat                 - Easy launcher (use this!)
- SETUP.bat                  - Setup script (run once)
- requirements.txt           - Python dependencies
- README.md                  - Full documentation
- QUICK_START.md            - Quick start guide
- Arduino firmware files    - For uploading to your Arduino

TROUBLESHOOTING
===============

Python Not Found:
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Then run SETUP.bat again

Application Won't Start:
- Make sure Python is installed: Open Command Prompt and type "python --version"
- Run SETUP.bat to install dependencies
- Check error messages in the console window

Dependencies Won't Install:
- Check your internet connection
- Try running: pip install --upgrade pip
- Then manually run: pip install -r requirements.txt

Shortcut Not Created:
- You can manually create a shortcut to LAUNCH.bat
- Or just double-click LAUNCH.bat to run the program

FOR MORE HELP
=============

See README.md for detailed documentation and troubleshooting.

================================================================================

