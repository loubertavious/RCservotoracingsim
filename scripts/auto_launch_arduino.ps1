# Auto-launch script for Arduino RC Servo Racing Sim
# This script monitors for Arduino connection and launches the program

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
$mainScript = Join-Path $projectRoot "main.py"
$pythonExe = "python"

# Function to check if Arduino is connected
function Test-ArduinoConnected {
    $ports = [System.IO.Ports.SerialPort]::GetPortNames()
    foreach ($port in $ports) {
        try {
            $serial = New-Object System.IO.Ports.SerialPort $port, 9600, None, 8, One
            $serial.ReadTimeout = 500
            $serial.Open()
            Start-Sleep -Milliseconds 100
            
            # Try to read Arduino's READY message
            if ($serial.BytesToRead -gt 0) {
                $line = $serial.ReadLine()
                if ($line -like "*READY*") {
                    $serial.Close()
                    return $true, $port
                }
            }
            $serial.Close()
        } catch {
            # Port might be in use or not an Arduino
        }
    }
    return $false, $null
}

# Wait for Arduino to be connected
Write-Host "Waiting for Arduino to be connected..."
Write-Host "Plug in your Arduino to start the program automatically."

while ($true) {
    $connected, $port = Test-ArduinoConnected
    if ($connected) {
        Write-Host "Arduino detected on $port! Launching program..."
        Start-Process $pythonExe -ArgumentList "`"$mainScript`"" -WorkingDirectory $projectRoot
        break
    }
    Start-Sleep -Seconds 2
}

