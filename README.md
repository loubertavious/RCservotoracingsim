# RC Servo Racing Sim Controller

A Python application that allows you to control servos on an Arduino using racing wheels or any game controller. Perfect for controlling RC cars with steering wheels and other input devices.

## Features

- **Controller Support**: Works with any game controller or racing wheel (Xbox, PlayStation, Logitech, etc.)
- **Real-time Input Display**: Shows wheel rotation angle and all controller input statistics
- **Flexible Mapping**: Map any controller input (axis, button, or hat) to any servo
- **Multiple Servos**: Control up to 16 servos simultaneously
- **Live Debugging**: Real-time display of all controller inputs for debugging

## Requirements

- Python 3.7 or higher
- Arduino (Uno, Nano, or compatible)
- Servo motors
- USB cable for Arduino
- Game controller or racing wheel

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Upload Arduino firmware:**
   - Open `arduino_servo_control.ino` in Arduino IDE
   - Connect your Arduino via USB
   - Select the correct board and port in Arduino IDE
   - Upload the sketch to your Arduino

3. **Wire your servos:**
   - Connect servo signal wires to pins 2-13 and A0-A3 (or modify `servoPins` array in the Arduino sketch)
   - Connect servo power (VCC) to 5V or external power supply
   - Connect servo ground (GND) to Arduino GND
   - **Note**: If using multiple servos, use an external power supply for the servos to avoid overloading the Arduino's 5V regulator

## Usage

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Connect your controller:**
   - Plug in your racing wheel or game controller
   - Click "Refresh" in the Controller section if it doesn't appear
   - Select your controller from the dropdown

3. **Connect to Arduino:**
   - Select the COM port where your Arduino is connected
   - Click "Connect"
   - Status should show "Connected" in green

4. **Map inputs to servos:**
   - Select a Servo ID (0-15)
   - Choose Input Type: axis, button, or hat
   - Enter the Input ID (axis number, button number, or hat number)
   - Click "Add Mapping"
   - The servo will now respond to that input in real-time

5. **Monitor inputs:**
   - The left panel shows all controller inputs in real-time
   - Wheel rotation angle is displayed in the right panel
   - Input statistics update automatically

## Input Types

- **Axis**: Analog inputs like steering wheel rotation, throttle, brake (values range from -1.0 to 1.0)
- **Button**: Digital inputs like buttons or triggers (0 or 1)
- **Hat**: D-pad or hat switch inputs (X and Y values: -1, 0, or 1)

## Servo Mapping

- **Axis to Servo**: Maps analog axis values to servo angles (0-180°)
  - Axis value -1.0 → Servo angle 0°
  - Axis value 0.0 → Servo angle 90°
  - Axis value 1.0 → Servo angle 180°

- **Button to Servo**: Maps button state to servo position
  - Button pressed → Servo angle 90°
  - Button released → Servo angle 0°

- **Hat to Servo**: Maps hat X value to servo angle
  - Hat left (-1) → Servo angle 0°
  - Hat center (0) → Servo angle 90°
  - Hat right (1) → Servo angle 180°

## Troubleshooting

- **Controller not detected**: Make sure it's plugged in and recognized by Windows. Try clicking "Refresh"
- **Arduino not connecting**: Check that the correct COM port is selected and no other program is using it
- **Servo not moving**: Verify wiring, check that servo is powered, and ensure the mapping is correct
- **Servo jittering**: This is normal for analog servos. Consider using digital servos or adding smoothing in the code

## Customization

### Changing Servo Pins

Edit the `servoPins` array in `arduino_servo_control.ino`:
```cpp
int servoPins[MAX_SERVOS] = {
  2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, A0, A1, A2, A3
};
```

### Adjusting Update Rate

In `main.py`, modify the delay in the `poll_loop` method:
```python
time.sleep(0.05)  # Change this value (0.05 = 20Hz)
```

### Changing Servo Range

Modify the angle calculation in the `process_mappings` method in `main.py` to adjust how input values map to servo angles.

## License

This project is open source and available for personal and educational use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

