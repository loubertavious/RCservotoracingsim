/*
 * RC Servo Racing Sim Controller - ESP32-S3 Firmware
 * Optimized for ESP32-S3 Development Board
 * 
 * This sketch receives servo commands via Serial and controls servos
 * Command format: "S<servo_id>:<angle>\n"
 * Example: "S0:90\n" sets servo 0 to 90 degrees
 * 
 * IMPORTANT NOTES FOR ESP32-S3:
 * - The ESP32Servo library can control up to 16 servos simultaneously
 * - ESP32-S3 has many GPIO pins available (avoid pins 19, 20, 43, 44 - USB pins)
 * - For multiple servos, use EXTERNAL POWER SUPPLY (5V, 2A+ recommended)
 *   Connect external power GND to ESP32-S3 GND, but DO NOT connect VCC to ESP32-S3 5V
 *   Servo signal wires go to the pins below, power/ground go to external supply
 * - ESP32-S3 uses 3.3V logic, but most servos work fine with 3.3V signals
 * - Serial communication is at 115200 baud (faster than Arduino Uno)
 */

#include <ESP32Servo.h>

// Maximum number of servos for ESP32-S3
#define MAX_SERVOS 16

// Servo objects
Servo servos[MAX_SERVOS];

// Servo pins for ESP32-S3
// Using GPIO pins (avoid USB pins: 19, 20, 43, 44)
// ESP32-S3 has many available GPIO pins
int servoPins[MAX_SERVOS] = {
  1, 2, 3, 4, 5, 6, 7, 8,      // GPIO 1-8
  9, 10, 11, 12, 13, 14, 15, 16 // GPIO 9-16
  // You can also use: 17, 18, 21, 35, 36, 37, 38, 39, 40, 41, 42, 45, 46, 47, 48
};

// Track which servos are attached
bool servoAttached[MAX_SERVOS] = {false};

void setup() {
  // Initialize serial communication at 115200 baud (ESP32-S3 default)
  Serial.begin(115200);
  
  // Wait for serial connection (important for USB serial on ESP32-S3)
  // Note: This will wait indefinitely if no Serial Monitor is open
  // Uncomment if you want to wait for Serial Monitor
  // while (!Serial) {
  //   delay(10);
  // }
  
  // Give ESP32-S3 a moment to initialize
  delay(100);
  
  // Send startup message (Python app will look for this)
  Serial.println("READY:RC Servo Controller - ESP32-S3");
  Serial.println("READY:Command format: S<servo_id>:<angle>");
  Serial.println("READY:Max servos: 16");
  Serial.println("READY:Baud rate: 115200");
  
  // Blink built-in LED if available (pin 38 on some ESP32-S3 boards)
  pinMode(38, OUTPUT);
  for(int i = 0; i < 3; i++) {
    digitalWrite(38, HIGH);
    delay(100);
    digitalWrite(38, LOW);
    delay(100);
  }
}

void loop() {
  // Check for incoming serial data
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    // Parse command: "S<servo_id>:<angle>"
    if (command.startsWith("S")) {
      int colonIndex = command.indexOf(':');
      if (colonIndex > 0) {
        int servoId = command.substring(1, colonIndex).toInt();
        int angle = command.substring(colonIndex + 1).toInt();
        
        // Validate servo ID and angle
        if (servoId >= 0 && servoId < MAX_SERVOS && angle >= 0 && angle <= 180) {
          // Attach servo if not already attached
          if (!servoAttached[servoId]) {
            servos[servoId].attach(servoPins[servoId]);
            servoAttached[servoId] = true;
          }
          
          // Set servo angle
          servos[servoId].write(angle);
          
          // Echo back confirmation (for debugging)
          Serial.print("OK:S");
          Serial.print(servoId);
          Serial.print(":");
          Serial.println(angle);
        }
      }
    }
  }
  
  // Small delay to prevent overwhelming the serial buffer
  delay(10);
}


