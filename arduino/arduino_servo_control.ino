/*
 * RC Servo Racing Sim Controller - Arduino Firmware
 * Optimized for Arduino UNO R3
 * 
 * This sketch receives servo commands via Serial and controls servos
 * Command format: "S<servo_id>:<angle>\n"
 * Example: "S0:90\n" sets servo 0 to 90 degrees
 * 
 * IMPORTANT NOTES FOR ARDUINO UNO R3:
 * - The Servo library can control up to 12 servos simultaneously
 * - Pins 0 and 1 are reserved for Serial communication (USB)
 * - Pin 13 has an onboard LED (can still be used for servo)
 * - For multiple servos, use EXTERNAL POWER SUPPLY (5V, 2A+ recommended)
 *   Connect external power GND to Arduino GND, but DO NOT connect VCC to Arduino 5V
 *   Servo signal wires go to the pins below, power/ground go to external supply
 */

#include <Servo.h>

// Maximum number of servos for Arduino UNO R3
// Note: Servo library supports up to 12 servos, but we allow 16 for flexibility
// If using more than 12, some servos may not work properly
#define MAX_SERVOS 12

// Servo objects
Servo servos[MAX_SERVOS];

// Servo pins for Arduino UNO R3
// Pins 2-13 (digital) + A0-A5 can be used as digital pins 14-19
// Avoid pins 0 and 1 (Serial communication)
// Pin 13 has onboard LED but can still be used
int servoPins[MAX_SERVOS] = {
  2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
  // For more servos, you can add: A0, A1, A2, A3, A4, A5
  // But remember: Servo library limit is 12 servos on UNO R3
};

// Track which servos are attached
bool servoAttached[MAX_SERVOS] = {false};

void setup() {
  // Initialize serial communication at 9600 baud
  Serial.begin(9600);
  
  // Wait for serial connection (important for USB serial on UNO R3)
  // Note: This will wait indefinitely if no Serial Monitor is open
  // Uncomment if you want to wait for Serial Monitor
  // while (!Serial) {
  //   delay(10);
  // }
  
  // Give Arduino a moment to initialize
  delay(100);
  
  // Send startup message (Python app will look for this)
  Serial.println("READY:RC Servo Controller - Arduino UNO R3");
  Serial.println("READY:Command format: S<servo_id>:<angle>");
  Serial.println("READY:Max servos: 12");
  
  // Blink onboard LED to show Arduino is running
  pinMode(13, OUTPUT);
  for(int i = 0; i < 3; i++) {
    digitalWrite(13, HIGH);
    delay(100);
    digitalWrite(13, LOW);
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

