Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
' Get parent directory (project root) since this script is in scripts/ subfolder
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)
projectRoot = fso.GetParentFolderName(scriptPath)
WshShell.CurrentDirectory = projectRoot
WshShell.Run "py main.py", 0, False
Set WshShell = Nothing
Set fso = Nothing


