# Arduino UNO R3 Setup Guide

## Quick Start

1. **Upload the Sketch:**
   - Open `arduino_servo_control.ino` in Arduino IDE
   - Select **Tools → Board → Arduino Uno**
   - Select **Tools → Port → [Your COM Port]** (e.g., COM3, COM4, etc.)
   - Click **Upload** (→ button)

2. **Connect Servos:**
   - **Signal wire** (usually orange/yellow) → Arduino pins 2-13
   - **Power wire** (usually red) → External 5V power supply **OR** Arduino 5V (for 1-2 servos only)
   - **Ground wire** (usually black/brown) → Arduino GND

3. **Power Considerations:**
   - **1-2 servos**: Can use Arduino 5V pin
   - **3+ servos**: **MUST use external 5V power supply** (2A+ recommended)
   - Connect external power supply GND to Arduino GND
   - **DO NOT** connect external power VCC to Arduino 5V pin

## Pin Assignments

| Servo ID | Arduino Pin | Notes |
|----------|-------------|-------|
| 0 | Pin 2 | Digital pin |
| 1 | Pin 3 | Digital pin |
| 2 | Pin 4 | Digital pin |
| 3 | Pin 5 | Digital pin |
| 4 | Pin 6 | Digital pin |
| 5 | Pin 7 | Digital pin |
| 6 | Pin 8 | Digital pin |
| 7 | Pin 9 | Digital pin |
| 8 | Pin 10 | Digital pin |
| 9 | Pin 11 | Digital pin |
| 10 | Pin 12 | Digital pin |
| 11 | Pin 13 | Digital pin (has onboard LED) |

## Wiring Diagram

```
Arduino UNO R3          Servo Motor
-----------             -----------
Pin 2  ──────── Signal ──────── Orange/Yellow
GND    ──────── Ground ──────── Black/Brown
5V     ──────── Power  ──────── Red (only for 1-2 servos)

For 3+ servos:
External Power Supply
-----------             
5V+    ──────── Power  ──────── Red (to all servos)
GND    ──────── Ground ──────── Black/Brown (to all servos)
       ──────── GND ──────── Arduino GND (common ground)
```

## Testing

1. Upload the sketch to your Arduino
2. Open Serial Monitor (Tools → Serial Monitor) at 9600 baud
3. You should see: "RC Servo Controller Ready - Arduino UNO R3"
4. In the Python application:
   - Select the COM port
   - Click "Connect"
   - Map a servo (e.g., Servo ID 0, Input Type: axis, Input ID: 0)
   - Move your controller or drag the on-screen wheel
   - The servo should move!

## Troubleshooting

### Servo Not Moving
- Check wiring (signal, power, ground)
- Verify servo is powered (LED on servo board if present)
- Check Serial Monitor for errors
- Try a different servo pin
- Ensure servo is not damaged (test with Arduino Servo sweep example)

### Arduino Not Connecting
- Check USB cable (data cable, not charge-only)
- Try a different USB port
- Check Device Manager for COM port
- Close other programs using the COM port (Arduino IDE Serial Monitor, etc.)
- Try unplugging and replugging the Arduino

### Servo Jittering
- Normal for analog servos
- Use external power supply if using multiple servos
- Add a capacitor (100-1000µF) across power supply
- Check for loose connections

### Multiple Servos Not Working
- Arduino UNO R3 Servo library supports max 12 servos
- Use external power supply for 3+ servos
- Check power supply amperage (each servo needs ~1A when moving)

## Advanced: Custom Pin Configuration

To change which pins control which servos, edit the `servoPins` array in `arduino_servo_control.ino`:

```cpp
int servoPins[MAX_SERVOS] = {
  2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
  // Change these numbers to match your wiring
};
```

**Important:** Avoid pins 0 and 1 (used for Serial/USB communication)

## Power Supply Recommendations

For controlling multiple servos (RC car steering, throttle, etc.):

- **Voltage:** 5V (or 6V for some servos - check servo specs)
- **Current:** 2A minimum, 5A+ recommended for multiple servos
- **Type:** Switching power supply or battery pack with voltage regulator
- **Connection:** 
  - Positive to servo red wires (common bus)
  - Negative to servo black wires AND Arduino GND (common ground)
  - Signal wires individually to Arduino pins

## Example: RC Car Setup

For a typical RC car with 2 servos (steering + throttle):

1. **Steering Servo:**
   - Signal → Pin 2
   - Power → External 5V supply
   - Ground → Common GND

2. **Throttle Servo:**
   - Signal → Pin 3
   - Power → External 5V supply (same bus as steering)
   - Ground → Common GND

3. **Mapping in Python App:**
   - Servo 0 (Pin 2): Map to controller axis 0 (steering wheel)
   - Servo 1 (Pin 3): Map to controller axis 1 (throttle) or button

