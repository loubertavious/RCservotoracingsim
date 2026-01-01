# Power Troubleshooting Guide

## Problem: Servos Drawing Too Much Power

If your Arduino can't connect or keeps disconnecting, the servos are likely drawing too much current from the Arduino's 5V regulator.

## Symptoms:
- ✅ Arduino appears on COM7 but connection fails
- ✅ Connection works but drops when servos move
- ✅ Arduino resets when servos are activated
- ✅ USB connection is unstable

## Solution: Use External Power Supply

### Quick Fix (1-2 servos):
1. **Disconnect servo power wires from Arduino 5V**
2. **Use Arduino 5V ONLY for signal** (keep signal wires connected)
3. **Power servos from separate 5V source:**
   - USB power bank
   - 5V wall adapter (2A+)
   - Battery pack with 5V regulator

### Proper Setup (3+ servos or RC car):

```
Arduino UNO R3          External 5V Supply        Servos
-----------             ------------------         ------
Pin 2-13 ──── Signal ─────────────────────────────── Orange/Yellow
GND      ──── GND ──────── GND ──── GND ─────────── Black/Brown
                                                    Red ──── 5V+ ──── External Supply
```

**IMPORTANT:**
- ✅ Connect Arduino GND to external supply GND (common ground)
- ✅ Connect servo signal wires to Arduino pins
- ✅ Connect servo power/ground to external supply
- ❌ **DO NOT** connect external supply 5V to Arduino 5V pin
- ❌ **DO NOT** power servos from Arduino 5V when using external supply

## Testing Without Servos

To verify your Python app is sending commands correctly:

1. **Disconnect all servos** from Arduino
2. **Connect to COM7** in the Python app
3. **Add a mapping** (e.g., Servo 0, axis 0)
4. **Move your controller** or drag the wheel
5. **Check the debug status** - you should see "OK:S0:XX" messages
6. If you see "OK" messages, Arduino is receiving commands!

## Power Supply Recommendations

### For Testing (1-2 servos):
- USB power bank (5V, 2A)
- Phone charger (5V, 2A+)
- Arduino can power 1-2 small servos, but not recommended

### For RC Car (2-4 servos):
- 5V switching power supply (5A recommended)
- 6V battery pack with voltage regulator
- LiPo battery with BEC (Battery Eliminator Circuit)

### Current Requirements:
- Small servo (SG90): ~0.5-1A when moving
- Standard servo: ~1-2A when moving
- Multiple servos: Add up the current needs
- **Always use 2x the calculated current** for safety margin

## Connection Test Procedure

1. **Disconnect all servos**
2. **Connect Arduino to COM7**
3. **Open Python app and connect**
4. **Check debug status** - should show "Connected: COM7"
5. **Add mapping and test** - should see "OK:S0:XX" in debug
6. **If OK messages appear**, Arduino is working!
7. **Now connect servos with external power**
8. **Test again** - servos should move

## Arduino Status Messages

When you connect, Arduino should send:
```
READY:RC Servo Controller - Arduino UNO R3
READY:Command format: S<servo_id>:<angle>
READY:Max servos: 12
```

When you send a command, Arduino responds:
```
OK:S0:90
```

If you see "OK" messages, your inputs ARE being seen by Arduino!

## Still Having Issues?

### Check These:
1. **USB Cable**: Use a data cable, not charge-only
2. **USB Port**: Try different USB port (avoid hubs)
3. **Arduino Power LED**: Should be lit
4. **Servo Wiring**: 
   - Signal (orange/yellow) → Arduino pin
   - Power (red) → External supply
   - Ground (black) → External supply AND Arduino GND
5. **External Supply**: 
   - Must be 5V (or 6V for some servos)
   - Must provide enough current (2A+ for multiple servos)
   - Must have common ground with Arduino

### Test Command Manually:

Open Serial Monitor in Arduino IDE (9600 baud) and type:
```
S0:90
```

You should see:
```
OK:S0:90
```

If this works, the problem is power, not communication!

