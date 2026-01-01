# Auto-Launch Setup Guide

This guide explains how to set up automatic launching of the RC Servo Racing Sim program when your Arduino is plugged in.

## Option 1: Simple Auto-Launch (Recommended)

1. **Run the installer:**
   - Double-click `install_auto_launch.vbs`
   - This will create a startup shortcut that monitors for Arduino connection

2. **How it works:**
   - The script runs in the background when Windows starts
   - It checks every 2 seconds for Arduino COM ports
   - When an Arduino is detected, it automatically launches the program

3. **To disable:**
   - Go to: `C:\Users\[YourUsername]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
   - Delete "RC Servo Racing Sim Auto-Launch.lnk"

## Option 2: Manual Launch Script

1. **Run manually when needed:**
   - Double-click `auto_launch_arduino.bat`
   - Plug in your Arduino
   - The program will launch automatically when detected

## Option 3: PowerShell Script (More Reliable)

1. **Run PowerShell script:**
   - Right-click `auto_launch_arduino.ps1` → "Run with PowerShell"
   - If you get an execution policy error, run this first:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

## Notes

- The script checks COM ports 3-20 (typical Arduino range)
- It waits for the Arduino's "READY" message to confirm it's connected
- The program will launch automatically once Arduino is detected
- You can still launch manually using `run.bat` or `main.py` directly

## Troubleshooting

- **Script doesn't detect Arduino:** Make sure the Arduino is powered and the correct drivers are installed
- **Program doesn't launch:** Check that Python is in your system PATH
- **Permission errors:** Run as Administrator if needed

