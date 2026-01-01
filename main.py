# Try to import pygame - it's optional (only needed for real game controllers)
# The virtual on-screen wheel works without pygame
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[INFO] pygame not available - real game controllers disabled")
    print("[INFO] Virtual on-screen wheel will still work")

import serial
import serial.tools.list_ports
import threading
import time
import math
from tkinter import *
from tkinter import ttk

class VirtualController:
    """Virtual controller for testing with on-screen wheel"""
    def __init__(self):
        self.name = "Virtual Controller (On-Screen Wheel)"
        self.axes = [0.0] * 4  # 4 axes: wheel, throttle, brake, etc.
        self.buttons = [False] * 16
        self.hats = [(0, 0)]
        self.wheel_angle = 0.0  # Continuous rotation, no limits
        self.throttle_angle = 0.0  # Continuous throttle angle (like steering)
        self.arrow_keys = {'left': False, 'right': False, 'up': False, 'down': False}
        self.arrow_key_sensitivity = 0.02  # Adjustable sensitivity
        self.auto_center_speed = 0.95  # Adjustable auto-center speed (0.0-1.0)
        self.max_angle = 180.0  # Maximum angle limit in degrees (0 = unlimited)
        self.max_throttle_angle = 180.0  # Maximum throttle angle limit in degrees (0 = unlimited)
        
    def get_info(self):
        return {
            'name': self.name,
            'axes': 4,
            'buttons': 16,
            'hats': 1
        }
    
    def get_state(self):
        # Map continuous angle to -1.0 to 1.0 for axis output
        # Use modulo to get current rotation within one full turn
        normalized = math.sin(math.radians(self.wheel_angle))
        self.axes[0] = normalized
        # Throttle works like steering - continuous angle tracking
        throttle_normalized = math.sin(math.radians(self.throttle_angle))
        self.axes[1] = throttle_normalized
        # Brake is the inverse of throttle (like steering rotation mapping)
        self.axes[2] = -throttle_normalized
        return {
            'axes': self.axes.copy(),
            'buttons': self.buttons.copy(),
            'hats': self.hats.copy()
        }
    
    def set_wheel_angle(self, angle):
        """Set wheel angle (with max angle limit if set)"""
        if self.max_angle > 0:
            # Apply max angle limit (symmetric: -max_angle to +max_angle)
            self.wheel_angle = max(-self.max_angle, min(self.max_angle, angle))
        else:
            # No limit (unlimited rotation)
            self.wheel_angle = angle
    
    def set_throttle_angle(self, angle):
        """Set throttle angle (with max angle limit if set) - works like steering"""
        if self.max_throttle_angle > 0:
            # Apply max angle limit (symmetric: -max_throttle_angle to +max_throttle_angle)
            self.throttle_angle = max(-self.max_throttle_angle, min(self.max_throttle_angle, angle))
        else:
            # No limit (unlimited rotation)
            self.throttle_angle = angle
    
    def set_arrow_key_sensitivity(self, sensitivity):
        """Set arrow key sensitivity (0.001 to 0.1)"""
        self.arrow_key_sensitivity = max(0.001, min(0.1, sensitivity))
    
    def set_max_throttle_angle(self, max_angle):
        """Set maximum throttle angle limit in degrees (0 = unlimited)"""
        self.max_throttle_angle = max(0.0, max_angle)
        # Apply limit to current angle if needed
        if self.max_throttle_angle > 0:
            self.set_throttle_angle(self.throttle_angle)
    
    def set_auto_center_speed(self, speed):
        """Set auto-center speed (0.0 to 1.0, higher = faster return)"""
        self.auto_center_speed = max(0.0, min(1.0, speed))
    
    def set_max_angle(self, max_angle):
        """Set maximum angle limit in degrees (0 = unlimited)"""
        self.max_angle = max(0.0, max_angle)
        # Apply limit to current angle if needed
        if self.max_angle > 0:
            self.set_wheel_angle(self.wheel_angle)
    
    def update_arrow_keys(self, left, right, up, down):
        """Update arrow key state for wheel and throttle (both work like steering)"""
        self.arrow_keys['left'] = left
        self.arrow_keys['right'] = right
        self.arrow_keys['up'] = up
        self.arrow_keys['down'] = down
        
        # Apply arrow key input to wheel with adjustable sensitivity
        if left and not right:
            self.set_wheel_angle(self.wheel_angle - self.arrow_key_sensitivity * 180)
        elif right and not left:
            self.set_wheel_angle(self.wheel_angle + self.arrow_key_sensitivity * 180)
        elif not left and not right:
            # Return to center slowly with adjustable speed
            if abs(self.wheel_angle) > 0.5:
                # Calculate target (nearest multiple of 360)
                target = round(self.wheel_angle / 360.0) * 360.0
                diff = target - self.wheel_angle
                self.set_wheel_angle(self.wheel_angle + diff * (1.0 - self.auto_center_speed))
            else:
                self.wheel_angle = 0.0
        
        # Apply arrow key input to throttle (works like steering - continuous rotation)
        if up and not down:
            self.set_throttle_angle(self.throttle_angle + self.arrow_key_sensitivity * 180)
        elif down and not up:
            self.set_throttle_angle(self.throttle_angle - self.arrow_key_sensitivity * 180)
        elif not up and not down:
            # Return to center slowly with adjustable speed
            if abs(self.throttle_angle) > 0.5:
                # Calculate target (nearest multiple of 360)
                target = round(self.throttle_angle / 360.0) * 360.0
                diff = target - self.throttle_angle
                self.set_throttle_angle(self.throttle_angle + diff * (1.0 - self.auto_center_speed))
            else:
                self.throttle_angle = 0.0

class WheelWidget(Canvas):
    """Interactive wheel widget that can be dragged"""
    def __init__(self, parent, virtual_controller, size=200, **kwargs):
        self.size = size
        self.radius = size // 2 - 10
        self.center_x = size // 2
        self.center_y = size // 2
        self.virtual_controller = virtual_controller
        
        Canvas.__init__(self, parent, width=size, height=size, **kwargs)
        self.config(bg='#2b2b2b', highlightthickness=0)
        
        self.angle = 0.0  # Current rotation angle in degrees
        self.dragging = False
        self.last_angle = 0.0
        
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw_wheel()
        
        # Auto-return to center
        self.auto_return_speed = 0.5
        self.auto_return_active = False
        
    def draw_wheel(self):
        """Draw the wheel"""
        self.delete("all")
        
        # Use angle modulo 360 for visual display (continuous rotation)
        display_angle = self.angle % 360
        if display_angle < 0:
            display_angle += 360
        
        # Draw outer circle
        self.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline='#ffffff',
            width=3,
            fill='#1a1a1a'
        )
        
        # Draw center circle
        self.create_oval(
            self.center_x - 15,
            self.center_y - 15,
            self.center_x + 15,
            self.center_y + 15,
            outline='#ffffff',
            width=2,
            fill='#333333'
        )
        
        # Draw spokes (rotating with wheel)
        spoke_length = self.radius - 20
        for i in range(4):
            angle_rad = math.radians(display_angle + i * 90)
            x1 = self.center_x + math.cos(angle_rad) * 20
            y1 = self.center_y + math.sin(angle_rad) * 20
            x2 = self.center_x + math.cos(angle_rad) * spoke_length
            y2 = self.center_y + math.sin(angle_rad) * spoke_length
            self.create_line(x1, y1, x2, y2, fill='#ffffff', width=2)
        
        # Draw top indicator
        indicator_angle = math.radians(display_angle)
        indicator_x = self.center_x + math.cos(indicator_angle) * (self.radius - 5)
        indicator_y = self.center_y + math.sin(indicator_angle) * (self.radius - 5)
        self.create_oval(
            indicator_x - 8,
            indicator_y - 8,
            indicator_x + 8,
            indicator_y + 8,
            fill='#00ff00',
            outline='#ffffff',
            width=2
        )
        
        # Draw angle text (show full rotations)
        rotations = int(self.angle / 360)
        remainder = self.angle % 360
        if remainder > 180:
            remainder -= 360
        if rotations != 0:
            angle_text = f"{remainder:.1f}° ({rotations:+d} rot)"
        else:
            angle_text = f"{remainder:.1f}°"
        self.create_text(
            self.center_x,
            self.center_y + self.radius + 20,
            text=angle_text,
            fill='#ffffff',
            font=("Arial", 11, "bold")
        )
    
    def on_click(self, event):
        """Handle mouse click"""
        self.dragging = True
        self.auto_return_active = False
        self.last_drag_angle = None  # Reset for continuous rotation tracking
        self.calculate_angle(event.x, event.y)
    
    def on_drag(self, event):
        """Handle mouse drag"""
        if self.dragging:
            self.calculate_angle(event.x, event.y)
    
    def on_release(self, event):
        """Handle mouse release"""
        self.dragging = False
        self.auto_return_active = True
    
    def calculate_angle(self, x, y):
        """Calculate angle from center to mouse position (continuous rotation)"""
        dx = x - self.center_x
        dy = y - self.center_y
        angle_rad = math.atan2(dy, dx)
        new_angle = math.degrees(angle_rad)
        
        # Handle continuous rotation - track relative movement
        if hasattr(self, 'last_drag_angle') and self.last_drag_angle is not None:
            # Calculate shortest rotation direction
            diff = new_angle - self.last_drag_angle
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360
            # Add the difference to current angle (allows continuous rotation)
            new_wheel_angle = self.angle + diff
        else:
            # First drag - align with current visual angle
            current_display = self.angle % 360
            if current_display < 0:
                current_display += 360
            # Calculate offset to match new angle
            offset = new_angle - current_display
            if offset > 180:
                offset -= 360
            elif offset < -180:
                offset += 360
            new_wheel_angle = self.angle + offset
        
        self.last_drag_angle = new_angle
        
        # Update virtual controller (will apply max angle limit if set)
        self.virtual_controller.set_wheel_angle(new_wheel_angle)
        self.angle = self.virtual_controller.wheel_angle  # Get the limited angle back
        
        self.draw_wheel()
    
    def set_angle(self, angle):
        """Set wheel angle programmatically (in degrees, respects max angle limit)"""
        # Use virtual controller's set_wheel_angle which applies max angle limit
        self.virtual_controller.set_wheel_angle(angle)
        self.angle = self.virtual_controller.wheel_angle  # Get the limited angle back
        self.draw_wheel()
    
    def update(self):
        """Update wheel (for auto-return to nearest 360° multiple)"""
        if self.auto_return_active and not self.dragging:
            vc = self.virtual_controller
            current_angle = vc.wheel_angle
            
            if abs(current_angle) > 0.5:
                # Calculate target (nearest multiple of 360)
                target = round(current_angle / 360.0) * 360.0
                diff = target - current_angle
                new_angle = current_angle + diff * (1.0 - vc.auto_center_speed)
                vc.set_wheel_angle(new_angle)
                self.angle = new_angle
                self.draw_wheel()
            else:
                vc.set_wheel_angle(0.0)
                self.angle = 0.0
                self.draw_wheel()

class ControllerManager:
    def __init__(self):
        self.pygame_available = PYGAME_AVAILABLE
        self.joysticks = []
        self.virtual_controller = VirtualController()
        
        if self.pygame_available:
            try:
                pygame.init()
                pygame.joystick.init()
                self.refresh_controllers()
            except Exception as e:
                print(f"[WARNING] Failed to initialize pygame: {e}")
                print("[INFO] Continuing with virtual controller only")
                self.pygame_available = False
                self.joysticks = []
        else:
            self.joysticks = []
        
    def refresh_controllers(self):
        """Refresh the list of connected controllers"""
        self.joysticks = []
        if not self.pygame_available:
            return 0
        
        try:
            for i in range(pygame.joystick.get_count()):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                self.joysticks.append(joystick)
        except Exception as e:
            print(f"[WARNING] Error refreshing controllers: {e}")
        return len(self.joysticks)
    
    def get_controller_info(self, index):
        """Get information about a controller"""
        # Check if it's the virtual controller (index = -1 or after all real controllers)
        if index == -1 or index == len(self.joysticks):
            return self.virtual_controller.get_info()
        
        if 0 <= index < len(self.joysticks):
            return {
                'name': self.joysticks[index].get_name(),
                'axes': self.joysticks[index].get_numaxes(),
                'buttons': self.joysticks[index].get_numbuttons(),
                'hats': self.joysticks[index].get_numhats()
            }
        return None
    
    def get_controller_state(self, index):
        """Get current state of a controller"""
        # Check if it's the virtual controller
        if index == -1 or index == len(self.joysticks):
            return self.virtual_controller.get_state()
        
        if 0 <= index < len(self.joysticks):
            joystick = self.joysticks[index]
            state = {
                'axes': [joystick.get_axis(i) for i in range(joystick.get_numaxes())],
                'buttons': [joystick.get_button(i) for i in range(joystick.get_numbuttons())],
                'hats': [joystick.get_hat(i) for i in range(joystick.get_numhats())]
            }
            return state
        return None

class ArduinoManager:
    def __init__(self):
        self.serial_connection = None
        self.connected = False
        self.port = None
        self.baudrate = 9600  # Default for Arduino Uno, will auto-detect ESP32-S3 (115200)
        self.last_response = ""
        self.commands_sent = 0
        self.commands_confirmed = 0
        
    def get_available_ports(self):
        """Get list of available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def auto_detect_baudrate(self, port):
        """Auto-detect baud rate by trying common values"""
        common_baudrates = [115200, 9600, 57600, 38400, 19200]
        
        for baud in common_baudrates:
            try:
                test_serial = serial.Serial(port, baud, timeout=1)
                time.sleep(0.5)  # Wait for device to send startup message
                
                # Check for READY message
                start_time = time.time()
                while time.time() - start_time < 2:
                    if test_serial.in_waiting > 0:
                        line = test_serial.readline().decode('utf-8', errors='ignore').strip()
                        if "READY" in line:
                            test_serial.close()
                            return baud
                test_serial.close()
            except:
                continue
        
        return None  # Could not detect, use default
    
    def connect(self, port, baudrate=9600):
        """Connect to Arduino/ESP32-S3 and verify it's responding"""
        try:
            if self.serial_connection:
                self.disconnect()
            
            print(f"Connecting to {port}...")
            
            # Try to auto-detect baud rate (ESP32-S3 uses 115200, Arduino Uno uses 9600)
            detected_baudrate = self.auto_detect_baudrate(port)
            if detected_baudrate:
                baudrate = detected_baudrate
                print(f"Auto-detected baud rate: {baudrate}")
            
            self.serial_connection = serial.Serial(port, baudrate, timeout=2)
            time.sleep(2)  # Wait for device to reset
            
            # Clear any leftover data
            self.serial_connection.reset_input_buffer()
            
            # Try to read Arduino's startup message
            startup_messages = []
            start_time = time.time()
            while time.time() - start_time < 3:  # Wait up to 3 seconds
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        startup_messages.append(line)
                        print(f"Arduino: {line}")
                        if "READY" in line:
                            break
                time.sleep(0.1)
            
            # Check if we got a READY message
            if any("READY" in msg for msg in startup_messages):
                print("✓ Arduino is responding!")
                self.connected = True
                self.port = port
                self.baudrate = baudrate
                self.commands_sent = 0
                self.commands_confirmed = 0
                return True
            else:
                print("⚠ Warning: Arduino didn't send READY message, but connection opened")
                print("  This might mean servos are drawing too much power")
                print("  Try disconnecting servos and reconnecting")
                self.connected = True  # Still mark as connected, but warn user
                self.port = port
                self.baudrate = baudrate
                return True
                
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
        self.connected = False
    
    def read_responses(self):
        """Read any responses from Arduino (non-blocking)"""
        responses = []
        if self.connected and self.serial_connection:
            try:
                while self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        responses.append(line)
                        if line.startswith("OK:"):
                            self.commands_confirmed += 1
            except:
                pass
        return responses
    
    def send_servo_command(self, servo_id, angle):
        """Send servo command to Arduino (servo_id: 0-15, angle: 0-180)"""
        if self.connected and self.serial_connection:
            try:
                # Format: "S<servo_id>:<angle>\n"
                command = f"S{servo_id}:{angle}\n"
                bytes_written = self.serial_connection.write(command.encode())
                self.commands_sent += 1
                
                # Try to read response (non-blocking)
                responses = self.read_responses()
                if responses:
                    self.last_response = responses[-1]
                
                return bytes_written > 0
            except Exception as e:
                print(f"Send error: {e}")
                return False
        return False
    
    def get_status(self):
        """Get connection status info"""
        if not self.connected:
            return "Disconnected"
        
        status = f"Connected: {self.port}"
        if self.commands_sent > 0:
            success_rate = (self.commands_confirmed / self.commands_sent) * 100
            status += f" | Commands: {self.commands_sent} sent, {self.commands_confirmed} confirmed ({success_rate:.0f}%)"
        
        return status

class ServoControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RC Servo Racing Sim Controller")
        self.root.geometry("1000x700")
        
        # Bring window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.focus_force()
        
        self.controller_manager = ControllerManager()
        self.arduino_manager = ArduinoManager()
        
        # Input to servo mappings: {servo_id: {'controller': index, 'input_type': 'axis/button/hat', 'input_id': id}}
        self.mappings = {}
        
        # Polling thread
        self.running = False
        self.poll_thread = None
        
        # Cache for stats to prevent unnecessary updates
        self.last_stats_text = ""
        
        self.setup_ui()
        self.start_polling()
        
        # Ensure window is visible and on top initially
        self.bring_to_front()
    
    def bring_to_front(self):
        """Bring the window to the front"""
        try:
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.update()
            self.root.attributes('-topmost', False)
            self.root.focus_force()
        except:
            pass
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(W, E, N, S))
        
        # Left panel - Controller info and stats
        left_panel = ttk.LabelFrame(main_frame, text="Controller Status", padding="10")
        left_panel.grid(row=0, column=0, sticky=(W, E, N, S), padx=(0, 10))
        
        # Controller selection
        ttk.Label(left_panel, text="Controller:").grid(row=0, column=0, sticky=W, pady=5)
        self.controller_var = StringVar()
        self.controller_combo = ttk.Combobox(left_panel, textvariable=self.controller_var, 
                                            state="readonly", width=30)
        self.controller_combo.grid(row=0, column=1, sticky=(W, E), pady=5)
        self.controller_combo.bind("<<ComboboxSelected>>", self.on_controller_selected)
        
        ttk.Button(left_panel, text="Refresh", command=self.refresh_controllers).grid(row=0, column=2, padx=5)
        
        # Controller info
        self.controller_info_text = Text(left_panel, height=8, width=50, wrap=WORD)
        self.controller_info_text.grid(row=1, column=0, columnspan=3, sticky=(W, E), pady=5)
        
        # Input stats display
        stats_label = ttk.Label(left_panel, text="Input Statistics:", font=("Arial", 10, "bold"))
        stats_label.grid(row=2, column=0, columnspan=3, sticky=W, pady=(10, 5))
        
        self.stats_text = Text(left_panel, height=15, width=50, wrap=WORD)
        self.stats_text.grid(row=3, column=0, columnspan=3, sticky=(W, E, N, S), pady=5)
        
        # Scrollbar for stats
        stats_scroll = ttk.Scrollbar(left_panel, orient=VERTICAL, command=self.stats_text.yview)
        stats_scroll.grid(row=3, column=3, sticky=(N, S))
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        # Visual axis bar charts
        axis_charts_label = ttk.Label(left_panel, text="Axis Visual Display:", font=("Arial", 10, "bold"))
        axis_charts_label.grid(row=4, column=0, columnspan=4, sticky=W, pady=(10, 5))
        
        axis_charts_frame = ttk.LabelFrame(left_panel, text="Real-Time Axis Values", padding="5")
        axis_charts_frame.grid(row=5, column=0, columnspan=4, sticky=(W, E), pady=5)
        
        # Axis colors and names
        axis_info = [
            ("Steering (Axis 0)", "#4A90E2", "#2E5C8A"),  # Blue gradient
            ("Throttle (Axis 1)", "#50C878", "#2E7D4E"),  # Green gradient
            ("Brake (Axis 2)", "#E74C3C", "#8B2635"),      # Red gradient
            ("Clutch (Axis 3)", "#FF8C00", "#CC7000")     # Orange gradient
        ]
        
        self.axis_charts = []
        for i, (name, color1, color2) in enumerate(axis_info):
            # Create frame for each axis
            axis_frame = ttk.Frame(axis_charts_frame)
            axis_frame.grid(row=i, column=0, sticky=(W, E), pady=3)
            
            # Axis label
            label = ttk.Label(axis_frame, text=name, font=("Arial", 9), width=20)
            label.grid(row=0, column=0, sticky=W, padx=5)
            
            # Canvas for gradient bar chart
            chart_canvas = Canvas(axis_frame, height=30, width=250, bg="#2b2b2b", highlightthickness=1, highlightbackground="#555555")
            chart_canvas.grid(row=0, column=1, sticky=(W, E), padx=5)
            
            # Value label
            value_label = ttk.Label(axis_frame, text="0.00", font=("Arial", 9), width=10)
            value_label.grid(row=0, column=2, padx=5)
            
            # Store canvas, colors, and label for updates
            self.axis_charts.append({
                'canvas': chart_canvas,
                'color1': color1,
                'color2': color2,
                'value_label': value_label,
                'name': name
            })
            
            axis_frame.columnconfigure(1, weight=1)
        
        axis_charts_frame.columnconfigure(0, weight=1)
        
        # Right panel - Tabbed interface
        right_panel = ttk.LabelFrame(main_frame, text="Controller & Servo Control", padding="10")
        right_panel.grid(row=0, column=1, sticky=(W, E, N, S))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(right_panel)
        notebook.grid(row=0, column=0, sticky=(W, E, N, S), pady=5)
        
        # Tab 1: Controller & Wheel
        controller_tab = ttk.Frame(notebook, padding="10")
        notebook.add(controller_tab, text="Controller & Wheel")
        
        # Arduino connection (at top of controller tab)
        arduino_frame = ttk.LabelFrame(controller_tab, text="Arduino Connection", padding="5")
        arduino_frame.grid(row=0, column=0, sticky=(W, E), pady=5)
        
        ttk.Label(arduino_frame, text="Port:").grid(row=0, column=0, sticky=W, pady=2)
        self.port_var = StringVar()
        self.port_combo = ttk.Combobox(arduino_frame, textvariable=self.port_var, width=20)
        self.port_combo.grid(row=0, column=1, sticky=(W, E), padx=5, pady=2)
        
        ttk.Button(arduino_frame, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=2)
        self.connect_btn = ttk.Button(arduino_frame, text="Connect", command=self.toggle_arduino_connection)
        self.connect_btn.grid(row=0, column=3, padx=2)
        
        self.connection_status = ttk.Label(arduino_frame, text="Disconnected", foreground="red")
        self.connection_status.grid(row=1, column=0, columnspan=4, pady=2)
        
        # Debug/Status info
        self.debug_status = ttk.Label(arduino_frame, text="", font=("Arial", 8), foreground="gray")
        self.debug_status.grid(row=2, column=0, columnspan=4, pady=2)
        
        # Interactive wheel widget (shown when virtual controller is selected)
        wheel_frame = ttk.LabelFrame(controller_tab, text="On-Screen Wheel (Testing)", padding="10")
        wheel_frame.grid(row=1, column=0, sticky=(W, E), pady=5)
        
        self.wheel_widget = WheelWidget(wheel_frame, self.controller_manager.virtual_controller, size=220)
        self.wheel_widget.grid(row=0, column=0, pady=5)
        
        ttk.Label(wheel_frame, text="Drag the wheel or use ← → arrow keys", 
                 font=("Arial", 9)).grid(row=1, column=0, pady=5)
        
        # Sensitivity and auto-center controls
        controls_frame = ttk.Frame(wheel_frame)
        controls_frame.grid(row=2, column=0, pady=5)
        
        # Arrow key sensitivity
        ttk.Label(controls_frame, text="Arrow Key Sensitivity:", font=("Arial", 9)).grid(row=0, column=0, sticky=W, padx=5)
        self.sensitivity_var = DoubleVar(value=0.02)
        sensitivity_scale = ttk.Scale(controls_frame, from_=0.001, to=0.1, variable=self.sensitivity_var, 
                                      orient=HORIZONTAL, length=150, command=self.on_sensitivity_change)
        sensitivity_scale.grid(row=0, column=1, padx=5)
        self.sensitivity_label = ttk.Label(controls_frame, text="0.02", font=("Arial", 8))
        self.sensitivity_label.grid(row=0, column=2, padx=5)
        
        # Auto-center speed
        ttk.Label(controls_frame, text="Auto-Center Speed:", font=("Arial", 9)).grid(row=1, column=0, sticky=W, padx=5, pady=2)
        self.autocenter_var = DoubleVar(value=0.95)
        autocenter_scale = ttk.Scale(controls_frame, from_=0.0, to=1.0, variable=self.autocenter_var,
                                    orient=HORIZONTAL, length=150, command=self.on_autocenter_change)
        autocenter_scale.grid(row=1, column=1, padx=5, pady=2)
        self.autocenter_label = ttk.Label(controls_frame, text="0.95", font=("Arial", 8))
        self.autocenter_label.grid(row=1, column=2, padx=5, pady=2)
        
        # Max angle limit
        ttk.Label(controls_frame, text="Max Angle Limit:", font=("Arial", 9)).grid(row=2, column=0, sticky=W, padx=5, pady=2)
        self.max_angle_var = DoubleVar(value=180.0)
        max_angle_scale = ttk.Scale(controls_frame, from_=0.0, to=720.0, variable=self.max_angle_var,
                                    orient=HORIZONTAL, length=150, command=self.on_max_angle_change)
        max_angle_scale.grid(row=2, column=1, padx=5, pady=2)
        self.max_angle_label = ttk.Label(controls_frame, text="180° (0=unlimited)", font=("Arial", 8))
        self.max_angle_label.grid(row=2, column=2, padx=5, pady=2)
        
        # Wheel rotation display (for all controllers)
        angle_frame = ttk.LabelFrame(controller_tab, text="Wheel Rotation Angle", padding="10")
        angle_frame.grid(row=2, column=0, sticky=(W, E), pady=5)
        
        self.wheel_angle_var = StringVar(value="0°")
        wheel_label = ttk.Label(angle_frame, textvariable=self.wheel_angle_var, 
                               font=("Arial", 24, "bold"))
        wheel_label.grid(row=0, column=0, pady=10)
        
        # Tab 2: Servo Mappings
        mapping_tab = ttk.Frame(notebook, padding="10")
        notebook.add(mapping_tab, text="Servo Mappings")
        
        # Servo mapping list - use a simple frame instead of LabelFrame to avoid blocking
        mapping_list_label = ttk.Label(mapping_tab, text="Servo Mappings", font=("Arial", 10, "bold"))
        mapping_list_label.grid(row=0, column=0, sticky=W, pady=(0, 5))
        
        # Treeview container with scrollbar
        tree_container = ttk.Frame(mapping_tab)
        tree_container.grid(row=1, column=0, sticky=(W, E, N, S), pady=2)
        
        columns = ("Servo", "Controller", "Input Type", "Input ID", "Value")
        self.mapping_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)
        for col in columns:
            self.mapping_tree.heading(col, text=col)
            if col == "Controller":
                self.mapping_tree.column(col, width=150)
            elif col == "Value":
                self.mapping_tree.column(col, width=80)
            else:
                self.mapping_tree.column(col, width=100)
        
        self.mapping_tree.grid(row=0, column=0, sticky=(W, E, N, S))
        
        mapping_scroll = ttk.Scrollbar(tree_container, orient=VERTICAL, command=self.mapping_tree.yview)
        mapping_scroll.grid(row=0, column=1, sticky=(N, S))
        self.mapping_tree.configure(yscrollcommand=mapping_scroll.set)
        
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)
        
        # Add mapping controls
        add_frame = ttk.LabelFrame(mapping_tab, text="Add/Remove Mappings", padding="5")
        add_frame.grid(row=2, column=0, sticky=(W, E), pady=5)
        
        # First row of controls
        ttk.Label(add_frame, text="Servo ID:").grid(row=0, column=0, padx=2, sticky=W)
        self.servo_id_var = StringVar(value="0")
        ttk.Spinbox(add_frame, from_=0, to=15, textvariable=self.servo_id_var, width=5).grid(row=0, column=1, padx=2, sticky=W)
        
        ttk.Label(add_frame, text="Type:").grid(row=0, column=2, padx=2, sticky=W)
        self.input_type_var = StringVar(value="axis")
        ttk.Combobox(add_frame, textvariable=self.input_type_var, values=["axis", "button", "hat"], 
                    state="readonly", width=7).grid(row=0, column=3, padx=2, sticky=W)
        
        ttk.Label(add_frame, text="ID:").grid(row=0, column=4, padx=2, sticky=W)
        self.input_id_var = StringVar(value="0")
        ttk.Spinbox(add_frame, from_=0, to=15, textvariable=self.input_id_var, width=5).grid(row=0, column=5, padx=2, sticky=W)
        
        # Second row of buttons
        ttk.Button(add_frame, text="Add Mapping", command=self.add_mapping).grid(row=1, column=0, columnspan=3, padx=2, pady=2, sticky=(W, E))
        ttk.Button(add_frame, text="Remove", command=self.remove_mapping).grid(row=1, column=3, columnspan=3, padx=2, pady=2, sticky=(W, E))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        left_panel.columnconfigure(1, weight=1)
        left_panel.rowconfigure(3, weight=1)
        axis_charts_frame.columnconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        controller_tab.columnconfigure(0, weight=1)
        mapping_tab.columnconfigure(0, weight=1)
        mapping_tab.rowconfigure(1, weight=1)
        wheel_frame.columnconfigure(0, weight=1)
        arduino_frame.columnconfigure(1, weight=1)
        
        # Keyboard bindings for arrow keys
        self.root.bind('<Left>', lambda e: self.on_arrow_key('left', True))
        self.root.bind('<KeyRelease-Left>', lambda e: self.on_arrow_key('left', False))
        self.root.bind('<Right>', lambda e: self.on_arrow_key('right', True))
        self.root.bind('<KeyRelease-Right>', lambda e: self.on_arrow_key('right', False))
        self.root.bind('<Up>', lambda e: self.on_arrow_key('up', True))
        self.root.bind('<KeyRelease-Up>', lambda e: self.on_arrow_key('up', False))
        self.root.bind('<Down>', lambda e: self.on_arrow_key('down', True))
        self.root.bind('<KeyRelease-Down>', lambda e: self.on_arrow_key('down', False))
        self.root.focus_set()  # Allow keyboard focus
        
        # Initialize
        self.refresh_controllers()
        self.refresh_ports()
        
        # Initialize sensitivity, auto-center, and max angle settings
        vc = self.controller_manager.virtual_controller
        vc.set_arrow_key_sensitivity(self.sensitivity_var.get())
        vc.set_auto_center_speed(self.autocenter_var.get())
        vc.set_max_angle(self.max_angle_var.get())
        vc.set_max_throttle_angle(180.0)  # Default throttle angle limit
        
    def refresh_controllers(self):
        """Refresh controller list"""
        count = self.controller_manager.refresh_controllers()
        controllers = []
        
        # Add virtual controller first
        controllers.append("V: Virtual Controller (On-Screen Wheel)")
        
        # Add real controllers
        for i in range(count):
            info = self.controller_manager.get_controller_info(i)
            controllers.append(f"{i}: {info['name']}")
        
        # Show message if pygame is not available
        if not self.controller_manager.pygame_available:
            # Add a note in the controller info
            self.controller_info_text.delete(1.0, END)
            self.controller_info_text.insert(1.0, 
                "⚠ pygame not available\n\n"
                "Real game controllers are disabled.\n"
                "The virtual on-screen wheel is still available.\n\n"
                "To enable real controllers:\n"
                "1. Install pygame: pip install pygame\n"
                "2. Restart the application\n\n"
                "Note: pygame installation may fail on some systems.\n"
                "The virtual controller works without pygame.")
        
        self.controller_combo['values'] = controllers
        if controllers:
            self.controller_combo.current(0)  # Select virtual controller by default
            self.on_controller_selected()
    
    def on_arrow_key(self, direction, pressed):
        """Handle arrow key press/release"""
        selection = self.controller_var.get()
        if not selection or not selection.startswith("V:"):
            return
        
        vc = self.controller_manager.virtual_controller
        if direction == 'left':
            vc.arrow_keys['left'] = pressed
        elif direction == 'right':
            vc.arrow_keys['right'] = pressed
        elif direction == 'up':
            vc.arrow_keys['up'] = pressed
        elif direction == 'down':
            vc.arrow_keys['down'] = pressed
    
    def on_sensitivity_change(self, value=None):
        """Update arrow key sensitivity"""
        sensitivity = self.sensitivity_var.get()
        self.controller_manager.virtual_controller.set_arrow_key_sensitivity(sensitivity)
        self.sensitivity_label.config(text=f"{sensitivity:.3f}")
    
    def on_autocenter_change(self, value=None):
        """Update auto-center speed"""
        speed = self.autocenter_var.get()
        self.controller_manager.virtual_controller.set_auto_center_speed(speed)
        self.autocenter_label.config(text=f"{speed:.2f}")
    
    def on_max_angle_change(self, value=None):
        """Update max angle limit"""
        max_angle = self.max_angle_var.get()
        self.controller_manager.virtual_controller.set_max_angle(max_angle)
        if max_angle == 0:
            self.max_angle_label.config(text="Unlimited")
        else:
            self.max_angle_label.config(text=f"{max_angle:.0f}°")
    
    def refresh_ports(self):
        """Refresh serial port list"""
        ports = self.arduino_manager.get_available_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)
    
    def on_controller_selected(self, event=None):
        """Update display when controller is selected"""
        self.update_controller_info()
        # Show/hide wheel widget based on selection
        selection = self.controller_var.get()
        if selection and selection.startswith("V:"):
            self.wheel_widget.grid()
        else:
            self.wheel_widget.grid_remove()
    
    def update_controller_info(self):
        """Update controller information display"""
        selection = self.controller_var.get()
        if not selection:
            return
        
        try:
            # Check if virtual controller
            if selection.startswith("V:"):
                index = -1
            else:
                index = int(selection.split(':')[0])
            
            info = self.controller_manager.get_controller_info(index)
            if info:
                text = f"Name: {info['name']}\n"
                text += f"Axes: {info['axes']}\n"
                text += f"Buttons: {info['buttons']}\n"
                text += f"Hats: {info['hats']}\n"
                self.controller_info_text.delete(1.0, END)
                self.controller_info_text.insert(1.0, text)
        except:
            pass
    
    def toggle_arduino_connection(self):
        """Toggle Arduino connection"""
        if self.arduino_manager.connected:
            self.arduino_manager.disconnect()
            self.connect_btn.config(text="Connect")
            self.connection_status.config(text="Disconnected", foreground="red")
            self.debug_status.config(text="")
        else:
            port = self.port_var.get()
            if port:
                if self.arduino_manager.connect(port):
                    self.connect_btn.config(text="Disconnect")
                    self.connection_status.config(text=f"Connected: {port}", foreground="green")
                    # Start reading responses in background
                    self.update_arduino_status()
                else:
                    self.connection_status.config(text="Connection Failed", foreground="red")
                    self.debug_status.config(text="Check if Arduino is powered and servos aren't drawing too much current")
    
    def update_arduino_status(self):
        """Update Arduino status display"""
        if self.arduino_manager.connected:
            # Read any responses
            responses = self.arduino_manager.read_responses()
            if responses:
                # Update debug status with last response
                last_response = responses[-1]
                if last_response.startswith("OK:"):
                    self.debug_status.config(text=f"✓ Last command confirmed: {last_response}", foreground="green")
                else:
                    self.debug_status.config(text=f"Arduino: {last_response}", foreground="blue")
            
            # Update status with command stats
            status_text = self.arduino_manager.get_status()
            if "Commands:" in status_text:
                self.debug_status.config(text=status_text.split("|")[1].strip() if "|" in status_text else "")
            
            # Schedule next update
            self.root.after(100, self.update_arduino_status)
    
    def add_mapping(self):
        """Add a new servo mapping"""
        try:
            servo_id = int(self.servo_id_var.get())
            input_type = self.input_type_var.get()
            input_id = int(self.input_id_var.get())
            
            # Get selected controller
            selection = self.controller_var.get()
            if not selection:
                print("No controller selected")
                return
            
            # Handle virtual controller
            if selection.startswith("V:"):
                controller_index = -1
            else:
                controller_index = int(selection.split(':')[0])
            
            # Add mapping
            self.mappings[servo_id] = {
                'controller': controller_index,
                'input_type': input_type,
                'input_id': input_id
            }
            
            print(f"Added mapping: Servo {servo_id} -> {input_type} {input_id} from controller {controller_index}")
            print(f"Total mappings: {len(self.mappings)}")
            
            # Force update on main thread
            self.root.after(0, self.update_mapping_display)
        except ValueError as e:
            print(f"Error adding mapping: {e}")
        except Exception as e:
            print(f"Unexpected error adding mapping: {e}")
    
    def remove_mapping(self):
        """Remove selected servo mapping"""
        selection = self.mapping_tree.selection()
        if selection:
            item = self.mapping_tree.item(selection[0])
            servo_id = int(item['values'][0])
            if servo_id in self.mappings:
                del self.mappings[servo_id]
                self.update_mapping_display()
    
    def update_mapping_display(self):
        """Update the mapping tree display"""
        try:
            # Clear existing items
            for item in self.mapping_tree.get_children():
                self.mapping_tree.delete(item)
            
            # Add current mappings
            for servo_id, mapping in sorted(self.mappings.items()):
                # Format controller name
                if mapping['controller'] == -1:
                    controller_name = "Virtual Controller"
                else:
                    controller_name = f"Controller {mapping['controller']}"
                
                input_type = mapping['input_type']
                input_id = mapping['input_id']
                
                # Get current value
                value = self.get_mapping_value(mapping)
                value_str = f"{value:.2f}" if isinstance(value, float) else str(value)
                
                # Insert into treeview
                item_id = self.mapping_tree.insert("", END, values=(servo_id, controller_name, input_type, input_id, value_str))
        except Exception as e:
            print(f"Error updating mapping display: {e}")
    
    def get_mapping_value(self, mapping):
        """Get current value for a mapping"""
        try:
            state = self.controller_manager.get_controller_state(mapping['controller'])
            if not state:
                return 0
            
            input_type = mapping['input_type']
            input_id = mapping['input_id']
            
            if input_type == 'axis':
                if input_id < len(state['axes']):
                    return state['axes'][input_id]
            elif input_type == 'button':
                if input_id < len(state['buttons']):
                    return 1 if state['buttons'][input_id] else 0
            elif input_type == 'hat':
                if input_id < len(state['hats']):
                    hat = state['hats'][input_id]
                    return hat[0]  # X value of hat
            
            return 0
        except:
            return 0
    
    def start_polling(self):
        """Start polling controllers for input"""
        self.running = True
        self.poll_thread = threading.Thread(target=self.poll_loop, daemon=True)
        self.poll_thread.start()
    
    def poll_loop(self):
        """Main polling loop"""
        while self.running:
            # Only pump pygame events if pygame is available
            if self.controller_manager.pygame_available:
                try:
                    pygame.event.pump()
                except:
                    pass
            
            # Update virtual controller arrow keys (continuous update while keys are held)
            selection = self.controller_var.get()
            if selection and selection.startswith("V:"):
                vc = self.controller_manager.virtual_controller
                # Apply arrow key input continuously with adjustable sensitivity
                vc.update_arrow_keys(vc.arrow_keys['left'], vc.arrow_keys['right'], 
                                    vc.arrow_keys['up'], vc.arrow_keys['down'])
                
                # Update wheel widget visual (continuous rotation)
                self.root.after(0, lambda: self.wheel_widget.set_angle(vc.wheel_angle))
            
            # Update stats
            self.update_stats()
            
            # Update visual axis charts
            self.root.after(0, self.update_axis_charts)
            
            # Update wheel angle (assuming axis 0 is steering wheel)
            self.update_wheel_angle()
            
            # Process mappings and send to Arduino
            self.process_mappings()
            
            # Read Arduino responses (non-blocking)
            if self.arduino_manager.connected:
                responses = self.arduino_manager.read_responses()
            
            # Update mapping display values only (don't recreate items, just update values)
            self.root.after(0, self.update_mapping_values)
            
            time.sleep(0.05)  # ~20Hz update rate
    
    def update_mapping_values(self):
        """Update only the values in existing mapping tree items (for real-time updates)"""
        try:
            # Update values for existing items
            for item_id in self.mapping_tree.get_children():
                item_values = list(self.mapping_tree.item(item_id, 'values'))
                if len(item_values) >= 4:
                    servo_id = int(item_values[0])
                    if servo_id in self.mappings:
                        mapping = self.mappings[servo_id]
                        # Get current value
                        value = self.get_mapping_value(mapping)
                        value_str = f"{value:.2f}" if isinstance(value, float) else str(value)
                        # Update the value column (index 4)
                        new_values = list(item_values)
                        if len(new_values) >= 5:
                            new_values[4] = value_str
                        else:
                            new_values.append(value_str)
                        self.mapping_tree.item(item_id, values=tuple(new_values))
        except Exception as e:
            # If update fails, do a full refresh
            self.update_mapping_display()
    
    def update_stats(self):
        """Update input statistics display"""
        selection = self.controller_var.get()
        if not selection:
            return
        
        try:
            # Handle virtual controller
            if selection.startswith("V:"):
                index = -1
            else:
                index = int(selection.split(':')[0])
            
            state = self.controller_manager.get_controller_state(index)
            if not state:
                return
            
            # Build text efficiently
            text = "RACING WHEEL INPUTS:\n"
            text += "=" * 30 + "\n\n"
            
            # Common racing wheel axes (only show first 4, which are typically steering, throttle, brake, clutch)
            axis_names = ["Steering", "Throttle", "Brake", "Clutch"]
            for i, value in enumerate(state['axes'][:4]):  # Only show first 4 axes
                # Always show axis 0 (steering), axis 1 (throttle), and axis 2 (brake)
                # Others only if significant
                if abs(value) > 0.001 or i <= 2:
                    axis_name = axis_names[i] if i < len(axis_names) else f"Axis {i}"
                    # Label with axis number for easy servo mapping
                    label = f"{axis_name} (Axis {i})"
                    # Convert steering to degrees for better readability
                    if i == 0:
                        angle = value * 180
                        text += f"{label:20s}: {value:7.3f} ({angle:+7.1f}°)\n"
                    else:
                        # Show throttle/brake/clutch as percentage
                        percent = (value + 1.0) * 50  # Convert -1 to 1 range to 0-100%
                        text += f"{label:20s}: {value:7.3f} ({percent:5.1f}%)\n"
            
            # Only show active buttons (pressed buttons)
            active_buttons = [i for i, pressed in enumerate(state['buttons']) if pressed]
            if active_buttons:
                text += "\nACTIVE BUTTONS:\n"
                for i in active_buttons:
                    text += f"  Button {i}\n"
            
            # Only show active hats (non-zero hats)
            active_hats = [(i, hat) for i, hat in enumerate(state['hats']) if hat[0] != 0 or hat[1] != 0]
            if active_hats:
                text += "\nACTIVE HATS:\n"
                for i, hat in active_hats:
                    text += f"  Hat {i}: ({hat[0]:+2d}, {hat[1]:+2d})\n"
            
            # Only update if text actually changed (prevents flashing)
            if text != self.last_stats_text:
                self.stats_text.delete(1.0, END)
                self.stats_text.insert(1.0, text)
                self.last_stats_text = text
        except Exception as e:
            # Silently fail to prevent error spam
            pass
    
    def update_axis_charts(self):
        """Update visual gradient bar chart sliders for each axis"""
        try:
            selection = self.controller_var.get()
            if not selection:
                return
            
            # Handle virtual controller
            if selection.startswith("V:"):
                index = -1
            else:
                index = int(selection.split(':')[0])
            
            state = self.controller_manager.get_controller_state(index)
            if not state or not state['axes']:
                return
            
            # Update each axis chart
            for i, chart in enumerate(self.axis_charts):
                if i < len(state['axes']):
                    value = state['axes'][i]
                    canvas = chart['canvas']
                    color1 = chart['color1']
                    color2 = chart['color2']
                    value_label = chart['value_label']
                    
                    # Clear canvas
                    canvas.delete("all")
                    
                    # Get canvas dimensions
                    canvas.update_idletasks()
                    width = canvas.winfo_width()
                    height = canvas.winfo_height()
                    if width < 10:
                        width = 250  # Default width
                    if height < 10:
                        height = 30  # Default height
                    
                    # Draw background track
                    margin = 3
                    track_y = height // 2
                    track_height = height - margin * 2
                    canvas.create_rectangle(margin, margin, width - margin, height - margin, 
                                          fill="#1a1a1a", outline="#555555", width=1)
                    
                    # Calculate bar position (-1.0 to 1.0 maps to left to right)
                    center_x = width / 2
                    bar_max_width = (width / 2) - margin * 2
                    bar_width = abs(value) * bar_max_width
                    
                    if abs(value) > 0.001:  # Only draw if significant
                        if value >= 0:
                            # Positive value - gradient bar extends right from center
                            bar_x1 = center_x
                            bar_x2 = center_x + bar_width
                            
                            # Create gradient effect (lighter to darker from center to edge)
                            steps = max(10, int(bar_width))
                            for step in range(steps):
                                x1 = bar_x1 + (step / steps) * bar_width
                                x2 = bar_x1 + ((step + 1) / steps) * bar_width
                                
                                # Interpolate color from color1 (lighter) to color2 (darker)
                                ratio = step / steps
                                r1, g1, b1 = tuple(int(color1[j:j+2], 16) for j in (1, 3, 5))
                                r2, g2, b2 = tuple(int(color2[j:j+2], 16) for j in (1, 3, 5))
                                r = int(r1 + (r2 - r1) * ratio)
                                g = int(g1 + (g2 - g1) * ratio)
                                b = int(b1 + (b2 - b1) * ratio)
                                color = f"#{r:02x}{g:02x}{b:02x}"
                                
                                canvas.create_rectangle(x1, margin, x2, height - margin,
                                                      fill=color, outline=color, width=0)
                        else:
                            # Negative value - gradient bar extends left from center
                            bar_x1 = center_x - bar_width
                            bar_x2 = center_x
                            
                            # Create gradient effect (lighter to darker from center to edge)
                            steps = max(10, int(bar_width))
                            for step in range(steps):
                                x1 = bar_x2 - ((step + 1) / steps) * bar_width
                                x2 = bar_x2 - (step / steps) * bar_width
                                
                                # Interpolate color from color1 (lighter) to color2 (darker)
                                ratio = step / steps
                                r1, g1, b1 = tuple(int(color1[j:j+2], 16) for j in (1, 3, 5))
                                r2, g2, b2 = tuple(int(color2[j:j+2], 16) for j in (1, 3, 5))
                                r = int(r1 + (r2 - r1) * ratio)
                                g = int(g1 + (g2 - g1) * ratio)
                                b = int(b1 + (b2 - b1) * ratio)
                                color = f"#{r:02x}{g:02x}{b:02x}"
                                
                                canvas.create_rectangle(x1, margin, x2, height - margin,
                                                      fill=color, outline=color, width=0)
                    
                    # Draw center line
                    canvas.create_line(center_x, margin, center_x, height - margin,
                                     fill="#666666", width=2)
                    
                    # Update value label
                    if i == 0:  # Steering - show degrees
                        angle = value * 180
                        value_label.config(text=f"{angle:+6.1f}°")
                    else:  # Others - show percentage
                        percent = (value + 1.0) * 50
                        value_label.config(text=f"{percent:5.1f}%")
        except Exception as e:
            # Silently fail to prevent error spam
            pass
    
    def update_wheel_angle(self):
        """Update wheel rotation angle display"""
        selection = self.controller_var.get()
        if not selection:
            return
        
        try:
            # Handle virtual controller
            if selection.startswith("V:"):
                index = -1
            else:
                index = int(selection.split(':')[0])
            
            state = self.controller_manager.get_controller_state(index)
            if not state or not state['axes']:
                return
            
            # Use first axis as steering wheel (typically axis 0)
            wheel_value = state['axes'][0]
            # For virtual controller, show actual continuous angle
            if selection.startswith("V:"):
                vc = self.controller_manager.virtual_controller
                rotations = int(vc.wheel_angle / 360)
                remainder = vc.wheel_angle % 360
                if remainder > 180:
                    remainder -= 360
                if rotations != 0:
                    self.wheel_angle_var.set(f"{remainder:+.1f}° ({rotations:+d} rot)")
                else:
                    self.wheel_angle_var.set(f"{remainder:+.1f}°")
            else:
                # Convert from -1.0 to 1.0 range to degrees (-180 to 180)
                angle = wheel_value * 180
                self.wheel_angle_var.set(f"{angle:+.1f}°")
        except:
            pass
    
    def process_mappings(self):
        """Process all mappings and send commands to Arduino"""
        for servo_id, mapping in self.mappings.items():
            value = self.get_mapping_value(mapping)
            
            # Convert value to servo angle (0-180)
            if mapping['input_type'] == 'axis':
                # Map from -1.0 to 1.0 to 0-180
                angle = int((value + 1.0) * 90)  # -1 -> 0, 0 -> 90, 1 -> 180
            elif mapping['input_type'] == 'button':
                # Button: 0 or 90 degrees (or could be 0/180)
                angle = 90 if value > 0 else 0
            elif mapping['input_type'] == 'hat':
                # Hat: map -1/0/1 to 0/90/180
                angle = int((value + 1.0) * 90)
            else:
                angle = 90  # Default center position
            
            # Clamp angle
            angle = max(0, min(180, angle))
            
            # Send to Arduino
            self.arduino_manager.send_servo_command(servo_id, angle)
    
    def on_closing(self):
        """Clean up on window close"""
        self.running = False
        if self.arduino_manager.connected:
            self.arduino_manager.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    
    # Bring window to front on startup
    root.lift()
    root.attributes('-topmost', True)
    root.update()
    root.attributes('-topmost', False)
    root.focus_force()
    
    app = ServoControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Ensure window stays on top initially
    root.after(100, lambda: root.focus_force())
    
    root.mainloop()

