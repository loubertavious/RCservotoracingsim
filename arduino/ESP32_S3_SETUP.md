# ESP32-S3 Setup Guide

This guide explains how to set up the RC Servo Racing Sim Controller for ESP32-S3.

## Hardware Requirements

- **ESP32-S3 Development Board** (any variant)
- **Servo motors** (standard 5V servos work fine with 3.3V signals)
- **External 5V power supply** (2A+ recommended for multiple servos)
- **USB cable** (for programming and serial communication)

## Pin Configuration

The ESP32-S3 firmware uses the following GPIO pins for servos:

- **Servo 0-7**: GPIO 1, 2, 3, 4, 5, 6, 7, 8
- **Servo 8-15**: GPIO 9, 10, 11, 12, 13, 14, 15, 16

### Available Alternative Pins

You can modify the `servoPins` array in the code to use:
- GPIO 17, 18, 21, 35, 36, 37, 38, 39, 40, 41, 42, 45, 46, 47, 48

### Pins to Avoid

- **GPIO 19, 20, 43, 44**: USB pins (do not use)
- **GPIO 0**: Boot button (can cause issues)
- **GPIO 46**: Strapping pin (use with caution)

## Software Setup

### 1. Install Arduino IDE with ESP32 Support

1. **Install Arduino IDE** (if not already installed)
   - Download from: https://www.arduino.cc/en/software

2. **Add ESP32 Board Support:**
   - Open Arduino IDE
   - Go to: **File → Preferences**
   - Add this URL to "Additional Board Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Click OK

3. **Install ESP32 Board Package:**
   - Go to: **Tools → Board → Boards Manager**
   - Search for "ESP32"
   - Install "esp32 by Espressif Systems"
   - Wait for installation to complete

4. **Install ESP32Servo Library:**
   - Go to: **Tools → Manage Libraries**
   - Search for "ESP32Servo"
   - Install "ESP32Servo by Kevin Harrington"

### 2. Upload Firmware

1. **Select Board:**
   - Go to: **Tools → Board → ESP32 Arduino → ESP32S3 Dev Module**
   - (Or your specific ESP32-S3 board variant)

2. **Configure Board Settings:**
   - **Upload Speed**: 921600 (or lower if you have issues)
   - **CPU Frequency**: 240MHz (or 160MHz)
   - **Flash Frequency**: 80MHz
   - **Flash Mode**: QIO
   - **Flash Size**: 4MB (or match your board)
   - **Partition Scheme**: Default 4MB with spiffs
   - **Core Debug Level**: None
   - **PSRAM**: Enabled (if your board has PSRAM)
   - **Port**: Select your ESP32-S3 COM port

3. **Open the Firmware:**
   - Open `arduino_servo_control_esp32s3.ino` in Arduino IDE

4. **Upload:**
   - Click the Upload button (→)
   - Wait for compilation and upload to complete
   - You should see "Hard resetting via RTS pin..." when done

### 3. Configure Python Application

The Python application needs to be configured for ESP32-S3's faster baud rate:

1. **Update Serial Baud Rate:**
   - The ESP32-S3 firmware uses **115200 baud** (instead of 9600 for Arduino Uno)
   - The Python code should auto-detect, but you can manually set it in the connection dialog

2. **Test Connection:**
   - Open Serial Monitor in Arduino IDE (115200 baud)
   - You should see: "READY:RC Servo Controller - ESP32-S3"
   - Close Serial Monitor before running Python app

## Wiring Diagram

```
ESP32-S3          External 5V Supply        Servos
-----------       ------------------         ------
GPIO 1-16  ──── Signal ───────────────────── Orange/Yellow
GND        ──── GND ──────── GND ─────────── Black/Brown
                                                    Red ──── 5V+ ──── External Supply
```

**IMPORTANT:**
- ✅ Connect ESP32-S3 GND to external supply GND (common ground)
- ✅ Connect servo signal wires to ESP32-S3 GPIO pins
- ✅ Connect servo power/ground to external supply
- ❌ **DO NOT** connect external supply 5V to ESP32-S3 5V pin
- ❌ **DO NOT** power servos from ESP32-S3 5V pin when using external supply

## Power Supply Recommendations

### For Testing (1-2 servos):
- USB power is usually sufficient
- No external supply needed

### For Production (3+ servos):
- **5V, 2A+ power supply** (wall adapter or battery pack)
- **Common ground** connection is critical
- Use a **capacitor** (1000µF) across power supply for stability

## Differences from Arduino Uno

| Feature | Arduino Uno | ESP32-S3 |
|---------|-------------|----------|
| Baud Rate | 9600 | 115200 |
| Max Servos | 12 | 16 |
| Logic Level | 5V | 3.3V |
| GPIO Pins | Limited | Many available |
| Speed | 16MHz | 240MHz |

## Troubleshooting

### Upload Issues
- **"Failed to connect"**: Hold BOOT button while clicking Upload
- **"A fatal error occurred"**: Try lower upload speed (115200)
- **Port not found**: Install ESP32-S3 USB drivers

### Servo Issues
- **Servos not moving**: Check wiring, verify external power is connected
- **Jittery servos**: Add capacitor (1000µF) to power supply
- **Only some servos work**: Check power supply current capacity

### Serial Communication
- **Connection fails**: Make sure baud rate is set to 115200 in Python
- **No response**: Close Serial Monitor in Arduino IDE
- **Timeout errors**: Check USB cable quality

## Advanced Configuration

### Custom Pin Assignment

Edit the `servoPins` array in `arduino_servo_control_esp32s3.ino`:

```cpp
int servoPins[MAX_SERVOS] = {
  1, 2, 3, 4, 5, 6, 7, 8,      // Your custom pins
  9, 10, 11, 12, 13, 14, 15, 16
};
```

### Changing Baud Rate

If you want to use 9600 baud (like Arduino Uno):

1. In firmware, change: `Serial.begin(115200);` to `Serial.begin(9600);`
2. Update Python code to use 9600 baud rate

## Testing

1. **Upload firmware** to ESP32-S3
2. **Open Serial Monitor** (115200 baud) - verify "READY" messages
3. **Close Serial Monitor**
4. **Run Python application** (`main.py` or `run.bat`)
5. **Select COM port** in the application
6. **Click Connect** - should show "Connected"
7. **Add a servo mapping** and test

## Notes

- ESP32-S3 is much faster than Arduino Uno
- Can handle more servos simultaneously
- 3.3V logic works fine with most 5V servos
- More GPIO pins available for expansion
- Built-in WiFi/Bluetooth (not used in this firmware, but available)

