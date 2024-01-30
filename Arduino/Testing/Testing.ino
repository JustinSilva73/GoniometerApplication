#include <Servo.h>

Servo myservo;
int currentAngle = 90; // Starting position

void setup() {
  myservo.attach(12); // Attach the servo to pin 12
  Serial.begin(115200); // Start serial communication at 115200 baud
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    int targetAngle = data.toInt(); // Convert the received string to an integer

    if (data.length() > 0 && targetAngle >= 0 && targetAngle <= 180) {
      moveToAngle(targetAngle);
      Serial.print("Moved to angle: ");
      Serial.println(targetAngle); 
    }
    while (Serial.available()) Serial.read(); // Clear the serial buffer
  }
}

void moveToAngle(int targetAngle) {
  currentAngle = targetAngle; // Update current angle
  myservo.write(currentAngle); // Move servo to the new angle
}
