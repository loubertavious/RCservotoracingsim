/*
 * Firmata-based Servo Control for Arduino
 * This uses the standard Firmata library - no custom code needed!
 * 
 * Instructions:
 * 1. Install Firmata library in Arduino IDE: Tools → Manage Libraries → Search "Firmata" → Install
 * 2. File → Examples → Firmata → StandardFirmata
 * 3. Upload that sketch to your Arduino
 * 4. Use the Python script to control servos
 * 
 * OR use this simplified version:
 */

#include <Servo.h>
#include <Firmata.h>

byte analogPin = 0;

void analogWriteCallback(byte pin, int value)
{
  if (IS_PIN_SERVO(pin)) {
    if (servoPinMap[pin] < MAX_SERVOS) {
      servos[servoPinMap[pin]].write(value);
    }
  }
}

void setup()
{
  Firmata.setFirmwareVersion(FIRMATA_MAJOR_VERSION, FIRMATA_MINOR_VERSION);
  Firmata.attach(ANALOG_MESSAGE, analogWriteCallback);
  Firmata.begin(57600);
}

void loop()
{
  while(Firmata.available()) {
    Firmata.processInput();
  }
}

