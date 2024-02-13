#include <Encoder.h>
#include <Servo.h>

class Calibration {
private:
    Encoder encoder;
    Servo motor
    int lowerLimit;
    int upperLimit;
    int tempLast = 0;

public:
    Calibration(int pinA, int pinB, Servo motor) : encoder(pinA, pinB), motor(motor), lowerLimit(0), upperLimit(0)  {}
    
    bool isLowerLimitReached() {
        if (encoder.read() < tempLast) {
            tempLast = encoder.read();
            return false;
        }
        return true;
    }

    bool isUpperLimitReached() {
        if (encoder.read() > tempLast) {
            tempLast = encoder.read();
            return false;
        }
        return true;
    }

    void findLimits() {
        while (!isLowerLimitReached()) {motor.write(89);}
        lowerLimit = encoder.read();

        while (!isUpperLimitReached()) {motor.write(91);}  
        upperLimit = encoder.read();
    }
};
