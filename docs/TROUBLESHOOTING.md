# Troubleshooting Guide

## Problem: LAUNCH.bat Closes Immediately

If the LAUNCH.bat window closes immediately without showing any messages, try these steps:

### Step 1: Run DIAGNOSE.bat

1. Double-click `DIAGNOSE.bat` in the program folder
2. This will check:
   - If Python is installed
   - If main.py exists
   - If dependencies are installed
   - If main.py can be imported

### Step 2: Check Common Issues

#### Python Not Found
- **Symptom**: Window closes immediately, no messages
- **Solution**: 
  - Install Python from https://www.python.org/downloads/
  - During installation, check "Add Python to PATH"
  - Restart your computer after installation
  - Run SETUP.bat again

#### main.py Not Found
- **Symptom**: Error message about main.py missing
- **Solution**:
  - Make sure you extracted ALL files from the ZIP
  - Check that main.py is in the same folder as LAUNCH.bat
  - Don't move or rename files after extraction

#### Python Version Too Old
- **Symptom**: Import errors or syntax errors
- **Solution**:
  - Need Python 3.7 or higher
  - Check version: `python --version`
  - Update Python if needed

#### Missing Dependencies
- **Symptom**: Import errors for 'serial' or other modules
- **Solution**:
  - Run SETUP.bat (installs dependencies automatically)
  - Or manually: `pip install pyserial`

#### Syntax Error in main.py
- **Symptom**: Python reports syntax error
- **Solution**:
  - The file may be corrupted
  - Re-download the package
  - Make sure you didn't edit main.py incorrectly

### Step 3: Run from Command Prompt

If the batch file still closes immediately:

1. Open Command Prompt (cmd.exe)
2. Navigate to the program folder:
   ```
   cd "C:\path\to\RC_Servo_Controller"
   ```
3. Run:
   ```
   python main.py
   ```
4. This will show the actual error message

### Step 4: Check Windows Event Viewer

1. Press Windows + R
2. Type `eventvwr` and press Enter
3. Check Windows Logs > Application
4. Look for Python errors around the time you tried to run the program

## Problem: Application Starts But Crashes

### Check Error Messages
- The window should stay open and show error messages
- Read the error message carefully
- Common errors are listed below

### Common Errors

#### "ModuleNotFoundError: No module named 'serial'"
- **Solution**: Run SETUP.bat or `pip install pyserial`

#### "ModuleNotFoundError: No module named 'pygame'"
- **Solution**: This is OK! The app works without pygame
- The virtual controller will still work
- See `PYGAME_TROUBLESHOOTING.md` if you want to install pygame

#### "PermissionError" or "Access Denied"
- **Solution**: 
  - Run as Administrator
  - Check file permissions
  - Make sure files aren't read-only

#### "COM port" errors
- **Solution**: 
  - This is normal if Arduino isn't connected
  - The app works without Arduino
  - Connect Arduino and select the correct COM port

## Getting Help

1. **Run DIAGNOSE.bat** - This will identify most issues
2. **Check the error message** - Read it carefully
3. **Try running from Command Prompt** - Shows actual Python errors
4. **Check documentation** - See other .md files in docs/ folder

## Still Having Issues?

If nothing works:

1. Make sure you have:
   - Windows 10 or later
   - Python 3.7 or higher installed
   - Internet connection (for first-time setup)

2. Try a fresh installation:
   - Delete the program folder
   - Extract the ZIP again
   - Run SETUP.bat
   - Run DIAGNOSE.bat to verify

3. Check Python installation:
   ```
   python --version
   python -m pip --version
   ```

If Python commands don't work, Python isn't installed correctly.

