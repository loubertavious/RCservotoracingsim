' Install auto-launch script to Windows Startup
' This will make the program auto-start when Arduino is detected

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the script directory
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batFile = scriptDir & "\auto_launch_arduino.bat"
startupFolder = WshShell.SpecialFolders("Startup")
shortcutPath = startupFolder & "\RC Servo Racing Sim Auto-Launch.lnk"

' Create shortcut in Startup folder
Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = batFile
shortcut.WorkingDirectory = scriptDir
shortcut.Description = "Auto-launch RC Servo Racing Sim when Arduino is connected"
shortcut.Save

MsgBox "Auto-launch installed successfully!" & vbCrLf & vbCrLf & _
       "The program will now automatically start when you plug in your Arduino." & vbCrLf & _
       "To disable, delete the shortcut from:" & vbCrLf & startupFolder, vbInformation, "Installation Complete"

