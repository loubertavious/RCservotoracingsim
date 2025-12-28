$WshShell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetPath = Join-Path $scriptDir "launch_app.vbs"
$shortcutPath = Join-Path $desktop "RC Servo Controller.lnk"

$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.WorkingDirectory = $scriptDir
$Shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,137"
$Shortcut.Description = "RC Servo Racing Sim Controller"
$Shortcut.Save()

Write-Host "Shortcut created successfully!"
Write-Host "Location: $shortcutPath"
Write-Host ""
Write-Host "You can now double-click 'RC Servo Controller' on your Desktop to launch the app."

