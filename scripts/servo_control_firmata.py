"""
Alternative Servo Control using Firmata Protocol
This doesn't require uploading custom Arduino code - just use StandardFirmata!

Setup:
1. In Arduino IDE: File → Examples → Firmata → StandardFirmata
2. Upload that to your Arduino
3. Run this script instead of main.py
"""

import pyfirmata
import time
import sys

class FirmataServoControl:
    def __init__(self, port=None):
        """Initialize Firmata connection to Arduino"""
        self.board = None
        self.port = port
        self.servos = {}
        
    def connect(self, port=None):
        """Connect to Arduino"""
        if port:
            self.port = port
        
        if not self.port:
            print("Error: No port specified")
            return False
        
        try:
            print(f"Connecting to Arduino on {self.port}...")
            self.board = pyfirmata.Arduino(self.port)
            print("Connected!")
            # Give it a moment to initialize
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def setup_servo(self, pin, servo_id=None):
        """Set up a servo on a specific pin"""
        if not self.board:
            print("Error: Not connected to Arduino")
            return False
        
        try:
            # Use servo_id as key, or pin number if not provided
            key = servo_id if servo_id is not None else pin
            self.servos[key] = self.board.get_pin(f'd:{pin}:s')  # 'd' = digital, ':s' = servo
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"Error setting up servo on pin {pin}: {e}")
            return False
    
    def set_servo_angle(self, servo_id, angle):
        """Set servo angle (0-180 degrees)"""
        if servo_id not in self.servos:
            print(f"Error: Servo {servo_id} not set up")
            return False
        
        try:
            # Clamp angle to 0-180
            angle = max(0, min(180, int(angle)))
            self.servos[servo_id].write(angle)
            return True
        except Exception as e:
            print(f"Error setting servo angle: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.board:
            self.board.exit()
            self.board = None

def list_ports():
    """List available serial ports"""
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    print("\nAvailable COM ports:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port.device} - {port.description}")
    return [p.device for p in ports]

if __name__ == "__main__":
    print("Firmata Servo Control")
    print("=" * 40)
    
    # List available ports
    ports = list_ports()
    
    if not ports:
        print("\nNo COM ports found. Make sure Arduino is connected.")
        sys.exit(1)
    
    # Let user select port
    if len(ports) == 1:
        selected_port = ports[0]
        print(f"\nUsing port: {selected_port}")
    else:
        print("\nSelect a port:")
        for i, port in enumerate(ports):
            print(f"  {i+1}. {port}")
        choice = input("Enter number: ")
        try:
            selected_port = ports[int(choice) - 1]
        except:
            print("Invalid choice")
            sys.exit(1)
    
    # Connect
    controller = FirmataServoControl()
    if not controller.connect(selected_port):
        print("Failed to connect")
        sys.exit(1)
    
    # Set up servo on pin 9 (you can change this)
    print("\nSetting up servo on pin 9...")
    controller.setup_servo(9, servo_id=0)
    
    # Test sequence
    print("\nTesting servo (pin 9)...")
    print("Moving to 0 degrees...")
    controller.set_servo_angle(0, 0)
    time.sleep(1)
    
    print("Moving to 90 degrees...")
    controller.set_servo_angle(0, 90)
    time.sleep(1)
    
    print("Moving to 180 degrees...")
    controller.set_servo_angle(0, 180)
    time.sleep(1)
    
    print("Moving to 90 degrees (center)...")
    controller.set_servo_angle(0, 90)
    
    print("\nTest complete! Servo should have moved.")
    print("You can now integrate this into your main application.")
    
    # Keep connection alive for a bit
    time.sleep(2)
    controller.disconnect()

