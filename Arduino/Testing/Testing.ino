#include <Servo.h>
#include <Arduino.h>

Servo myservo;

int currentAngle = 90; // Starting position

struct FlightData {
  String angle;
  int time;
};

FlightData flight_data[100]; // Adjust the size as needed
int flight_data_count = 0;

   void setup() {
  myservo.attach(12); // Attach the servo to pin 12
  Serial.begin(115200); // Start serial communication at 115200 baud
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
<<<<<<< Updated upstream
    int targetAngle = data.toInt(); // Convert the received string to an integer

    if (data.length() > 0 && targetAngle >= 0 && targetAngle <= 180) {
      moveToAngle(targetAngle);
      Serial.print("Moved to angle: ");
<<<<<<< Updated upstream
      Serial.println(targetAngle); // Send confirmation back to Python
=======
      Serial.println(targetAngle); 
=======
    if (data == "Files") {
      while (data != "end") {
        data = Serial.readStringUntil('\n');
        if (data != "end") {
          int angle = data.substring(data.indexOf(':') + 1).toInt();
          int time = data.substring(data.indexOf(':') + 1).toInt();
          flight_data[flight_data_count] = {angle, time};
          flight_data_count++;
        }
      }
>>>>>>> Stashed changes
>>>>>>> Stashed changes
    }
  }
  
  else if (data.length() > 0 && targetAngle >= 0 && targetAngle <= 180) {
    moveToAngle(targetAngle);
    Serial.print("Moved to angle: ");
    Serial.println(targetAngle);
  }
  while (Serial.available()) Serial.read()){; // Clear the serial buffer
  }
}

void moveToAngle(int targetAngle) {
  currentAngle = targetAngle; // Update current angle
  myservo.write(currentAngle); // Move servo to the new angle
}
