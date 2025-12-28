import pygame
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
        self.wheel_angle = 0.0  # -1.0 to 1.0
        self.arrow_keys = {'left': False, 'right': False}
        
    def get_info(self):
        return {
            'name': self.name,
            'axes': 4,
            'buttons': 16,
            'hats': 1
        }
    
    def get_state(self):
        return {
            'axes': self.axes.copy(),
            'buttons': self.buttons.copy(),
            'hats': self.hats.copy()
        }
    
    def set_wheel_angle(self, angle):
        """Set wheel angle (-1.0 to 1.0)"""
        self.wheel_angle = max(-1.0, min(1.0, angle))
        self.axes[0] = self.wheel_angle
    
    def update_arrow_keys(self, left, right):
        """Update arrow key state"""
        self.arrow_keys['left'] = left
        self.arrow_keys['right'] = right
        # Apply arrow key input to wheel
        if left and not right:
            self.set_wheel_angle(self.wheel_angle - 0.05)
        elif right and not left:
            self.set_wheel_angle(self.wheel_angle + 0.05)
        elif not left and not right:
            # Return to center slowly
            if abs(self.wheel_angle) > 0.01:
                self.set_wheel_angle(self.wheel_angle * 0.95)

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
            angle_rad = math.radians(self.angle + i * 90)
            x1 = self.center_x + math.cos(angle_rad) * 20
            y1 = self.center_y + math.sin(angle_rad) * 20
            x2 = self.center_x + math.cos(angle_rad) * spoke_length
            y2 = self.center_y + math.sin(angle_rad) * spoke_length
            self.create_line(x1, y1, x2, y2, fill='#ffffff', width=2)
        
        # Draw top indicator
        indicator_angle = math.radians(self.angle)
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
        
        # Draw angle text
        angle_text = f"{self.angle:.1f}°"
        self.create_text(
            self.center_x,
            self.center_y + self.radius + 20,
            text=angle_text,
            fill='#ffffff',
            font=("Arial", 12, "bold")
        )
    
    def on_click(self, event):
        """Handle mouse click"""
        self.dragging = True
        self.auto_return_active = False
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
        """Calculate angle from center to mouse position"""
        dx = x - self.center_x
        dy = y - self.center_y
        angle_rad = math.atan2(dy, dx)
        self.angle = math.degrees(angle_rad)
        
        # Normalize to -180 to 180
        if self.angle > 180:
            self.angle -= 360
        if self.angle < -180:
            self.angle += 360
        
        # Update virtual controller
        normalized = self.angle / 180.0  # -1.0 to 1.0
        self.virtual_controller.set_wheel_angle(normalized)
        
        self.draw_wheel()
    
    def set_angle(self, angle):
        """Set wheel angle programmatically (in degrees)"""
        self.angle = max(-180, min(180, angle))
        normalized = self.angle / 180.0
        self.virtual_controller.set_wheel_angle(normalized)
        self.draw_wheel()
    
    def update(self):
        """Update wheel (for auto-return)"""
        if self.auto_return_active and not self.dragging:
            if abs(self.angle) > 0.5:
                self.angle *= 0.95
                normalized = self.angle / 180.0
                self.virtual_controller.set_wheel_angle(normalized)
                self.draw_wheel()
            elif abs(self.angle) <= 0.5:
                self.angle = 0.0
                self.virtual_controller.set_wheel_angle(0.0)
                self.draw_wheel()

class ControllerManager:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joysticks = []
        self.virtual_controller = VirtualController()
        self.refresh_controllers()
        
    def refresh_controllers(self):
        """Refresh the list of connected controllers"""
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
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
        self.baudrate = 9600
        self.last_response = ""
        self.commands_sent = 0
        self.commands_confirmed = 0
        
    def get_available_ports(self):
        """Get list of available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port, baudrate=9600):
        """Connect to Arduino and verify it's responding"""
        try:
            if self.serial_connection:
                self.disconnect()
            
            print(f"Connecting to {port}...")
            self.serial_connection = serial.Serial(port, baudrate, timeout=2)
            time.sleep(2)  # Wait for Arduino to reset
            
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
        
        self.controller_manager = ControllerManager()
        self.arduino_manager = ArduinoManager()
        
        # Input to servo mappings: {servo_id: {'controller': index, 'input_type': 'axis/button/hat', 'input_id': id}}
        self.mappings = {}
        
        # Polling thread
        self.running = False
        self.poll_thread = None
        
        self.setup_ui()
        self.start_polling()
        
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
        
        # Right panel - Servo mapping
        right_panel = ttk.LabelFrame(main_frame, text="Servo Mapping", padding="10")
        right_panel.grid(row=0, column=1, sticky=(W, E, N, S))
        
        # Arduino connection
        arduino_frame = ttk.LabelFrame(right_panel, text="Arduino Connection", padding="5")
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
        
        # Servo mappings
        mapping_frame = ttk.LabelFrame(right_panel, text="Servo Mappings", padding="5")
        mapping_frame.grid(row=1, column=0, sticky=(W, E, N, S), pady=5)
        
        # Servo mapping list
        columns = ("Servo", "Controller", "Input Type", "Input ID", "Value")
        self.mapping_tree = ttk.Treeview(mapping_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.mapping_tree.heading(col, text=col)
            self.mapping_tree.column(col, width=100)
        
        self.mapping_tree.grid(row=0, column=0, columnspan=3, sticky=(W, E, N, S))
        
        mapping_scroll = ttk.Scrollbar(mapping_frame, orient=VERTICAL, command=self.mapping_tree.yview)
        mapping_scroll.grid(row=0, column=3, sticky=(N, S))
        self.mapping_tree.configure(yscrollcommand=mapping_scroll.set)
        
        # Add mapping controls
        add_frame = ttk.Frame(mapping_frame)
        add_frame.grid(row=1, column=0, columnspan=4, sticky=(W, E), pady=5)
        
        ttk.Label(add_frame, text="Servo ID:").grid(row=0, column=0, padx=2)
        self.servo_id_var = StringVar(value="0")
        ttk.Spinbox(add_frame, from_=0, to=15, textvariable=self.servo_id_var, width=5).grid(row=0, column=1, padx=2)
        
        ttk.Label(add_frame, text="Input:").grid(row=0, column=2, padx=2)
        self.input_type_var = StringVar(value="axis")
        ttk.Combobox(add_frame, textvariable=self.input_type_var, values=["axis", "button", "hat"], 
                    state="readonly", width=8).grid(row=0, column=3, padx=2)
        
        self.input_id_var = StringVar(value="0")
        ttk.Spinbox(add_frame, from_=0, to=15, textvariable=self.input_id_var, width=5).grid(row=0, column=4, padx=2)
        
        ttk.Button(add_frame, text="Add Mapping", command=self.add_mapping).grid(row=0, column=5, padx=5)
        ttk.Button(add_frame, text="Remove", command=self.remove_mapping).grid(row=0, column=6, padx=5)
        
        # Interactive wheel widget (shown when virtual controller is selected)
        wheel_frame = ttk.LabelFrame(right_panel, text="On-Screen Wheel (Testing)", padding="10")
        wheel_frame.grid(row=2, column=0, sticky=(W, E), pady=5)
        
        self.wheel_widget = WheelWidget(wheel_frame, self.controller_manager.virtual_controller, size=220)
        self.wheel_widget.grid(row=0, column=0, pady=5)
        
        ttk.Label(wheel_frame, text="Drag the wheel or use ← → arrow keys", 
                 font=("Arial", 9)).grid(row=1, column=0, pady=5)
        
        # Wheel rotation display (for all controllers)
        angle_frame = ttk.LabelFrame(right_panel, text="Wheel Rotation Angle", padding="10")
        angle_frame.grid(row=3, column=0, sticky=(W, E), pady=5)
        
        self.wheel_angle_var = StringVar(value="0°")
        wheel_label = ttk.Label(angle_frame, textvariable=self.wheel_angle_var, 
                               font=("Arial", 24, "bold"))
        wheel_label.grid(row=0, column=0, pady=10)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        left_panel.columnconfigure(1, weight=1)
        left_panel.rowconfigure(3, weight=1)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        mapping_frame.columnconfigure(0, weight=1)
        mapping_frame.rowconfigure(0, weight=1)
        
        # Keyboard bindings for arrow keys
        self.root.bind('<Left>', lambda e: self.on_arrow_key('left', True))
        self.root.bind('<KeyRelease-Left>', lambda e: self.on_arrow_key('left', False))
        self.root.bind('<Right>', lambda e: self.on_arrow_key('right', True))
        self.root.bind('<KeyRelease-Right>', lambda e: self.on_arrow_key('right', False))
        self.root.focus_set()  # Allow keyboard focus
        
        # Initialize
        self.refresh_controllers()
        self.refresh_ports()
        
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
            
            self.update_mapping_display()
        except ValueError:
            pass
    
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
        # Clear existing items
        for item in self.mapping_tree.get_children():
            self.mapping_tree.delete(item)
        
        # Add current mappings
        for servo_id, mapping in self.mappings.items():
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
            
            self.mapping_tree.insert("", END, values=(servo_id, controller_name, input_type, input_id, value_str))
    
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
            pygame.event.pump()
            
            # Update virtual controller arrow keys (continuous update while keys are held)
            selection = self.controller_var.get()
            if selection and selection.startswith("V:"):
                vc = self.controller_manager.virtual_controller
                # Apply arrow key input continuously
                if vc.arrow_keys['left'] and not vc.arrow_keys['right']:
                    vc.set_wheel_angle(vc.wheel_angle - 0.02)
                elif vc.arrow_keys['right'] and not vc.arrow_keys['left']:
                    vc.set_wheel_angle(vc.wheel_angle + 0.02)
                elif not vc.arrow_keys['left'] and not vc.arrow_keys['right']:
                    # Return to center slowly (only if not dragging)
                    if not self.wheel_widget.dragging and abs(vc.wheel_angle) > 0.01:
                        vc.set_wheel_angle(vc.wheel_angle * 0.95)
                
                # Update wheel widget visual
                angle_deg = vc.wheel_angle * 180
                self.root.after(0, lambda: self.wheel_widget.set_angle(angle_deg))
            
            # Update stats
            self.update_stats()
            
            # Update wheel angle (assuming axis 0 is steering wheel)
            self.update_wheel_angle()
            
            # Process mappings and send to Arduino
            self.process_mappings()
            
            # Read Arduino responses (non-blocking)
            if self.arduino_manager.connected:
                responses = self.arduino_manager.read_responses()
            
            # Update mapping display
            self.root.after(0, self.update_mapping_display)
            
            time.sleep(0.05)  # ~20Hz update rate
    
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
            
            text = "AXES:\n"
            for i, value in enumerate(state['axes']):
                text += f"  Axis {i}: {value:6.3f}\n"
            
            text += "\nBUTTONS:\n"
            for i, pressed in enumerate(state['buttons']):
                text += f"  Button {i}: {'PRESSED' if pressed else 'released'}\n"
            
            text += "\nHATS:\n"
            for i, hat in enumerate(state['hats']):
                text += f"  Hat {i}: ({hat[0]}, {hat[1]})\n"
            
            self.stats_text.delete(1.0, END)
            self.stats_text.insert(1.0, text)
        except:
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
    app = ServoControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

