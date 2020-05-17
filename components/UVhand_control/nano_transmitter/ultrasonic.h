/*
  HCSR04 - Library for arduino, for HC-SR04 ultrasonic distance sensor.
  Created by Martin Sosic, June 11, 2016.
*/

#ifndef __ULTRASONIC_H
#define __ULTRASONIC_H

#include "Arduino.h"

class Ultrasonic {
 public:
    /**
     * @param triggerPin  Digital pin that is used for controlling sensor (output).
     * @param echoPin  Digital pin that is used to get information from sensor (input).
     */
    Ultrasonic(int triggerPin, int echoPin);

    /**
     * Measures distance by sending ultrasonic waves and measuring time it takes them to return.
     * @returns Distance in centimeters, or negative value if distance is greater than 400cm.
     */
    int measure();

 private:
    int triggerPin, echoPin;
};

#endif // __ULTRASONIC_H
