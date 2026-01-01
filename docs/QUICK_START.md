# Quick Start Guide

## First Time Setup

1. **Run SETUP.bat** (double-click it)
   - This will check Python installation
   - Install required dependencies
   - Create desktop and Start Menu shortcuts

2. **Launch the application:**
   - Double-click "RC Servo Controller" on your Desktop, OR
   - Double-click `LAUNCH.bat` in this folder

## Launch the Application

### Option 1: Desktop Shortcut (Easiest)
- Double-click "RC Servo Controller" on your Desktop
- Created automatically by SETUP.bat

### Option 2: LAUNCH.bat (Recommended)
- Double-click `LAUNCH.bat` to launch the application
- Shows helpful status messages
- Automatically installs dependencies if needed

### Option 3: run.bat (Legacy)
- Located in `scripts/` folder (older launcher, still works)

### Option 4: Command Line
```bash
py main.py
```

## Creating a Desktop Shortcut

### Automatic (Recommended):
1. Double-click `SETUP.bat`
2. Shortcuts will be created on Desktop and Start Menu

### Manual:
1. Right-click on `LAUNCH.bat`
2. Select "Create shortcut"
3. Drag shortcut to Desktop

## Troubleshooting

### Shortcut doesn't work:
- Make sure Python is installed and `py` command works
- Try using `scripts/run.bat` instead
- Check that `main.py` is in the root folder

### App won't start:
- Run `run.bat` to see error messages
- Make sure dependencies are installed: `pip install -r requirements.txt`


