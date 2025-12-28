# Quick Start Guide

## Launch the Application

### Option 1: Double-Click Shortcut (Easiest)
1. Run `create_shortcut.bat` once to create a desktop shortcut
2. Double-click the "RC Servo Controller" shortcut on your desktop
3. The app will launch without showing a console window

### Option 2: Double-Click Batch File
- Double-click `run.bat` to launch the application
- A console window will show status messages

### Option 3: Double-Click VBS Script
- Double-click `launch_app.vbs` to launch silently (no console window)

### Option 4: Command Line
```bash
py main.py
```

## Creating a Desktop Shortcut

### Automatic (Recommended):
1. Double-click `create_shortcut.bat`
2. A shortcut will be created on your Desktop
3. Double-click the shortcut to launch

### Manual:
1. Right-click on `launch_app.vbs`
2. Select "Create shortcut"
3. Right-click the new shortcut → Properties
4. Change icon if desired
5. Drag shortcut to Desktop

## Troubleshooting

### Shortcut doesn't work:
- Make sure Python is installed and `py` command works
- Try using `run.bat` instead
- Check that `main.py` is in the same folder

### App won't start:
- Run `run.bat` to see error messages
- Make sure dependencies are installed: `pip install -r requirements.txt`

