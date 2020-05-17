/*
  HCSR04 - Library for arduino, for HC-SR04 ultrasonic distance sensor.
  Created by Martin Sosic, June 11, 2016.
*/
#ifndef __ULTRASONIC_CPP
#define __ULTRASONIC_CPP
#include "Arduino.h"
#include "ultrasonic.h"

#define TRIG_PIN 6
#define ECHO_PIN 7

#define MAX_WAIT 30000 //us, 30ms --> max timeout from echo pulse
#define MAX_DISTANCE 150 //cm

Ultrasonic::Ultrasonic(int triggerPin = TRIG_PIN,
                       int echoPin = ECHO_PIN) {
    this->triggerPin = triggerPin;
    this->echoPin = echoPin;
    //---------------------- Setup -----------------------
    pinMode(this->triggerPin, OUTPUT);
    pinMode(this->echoPin, INPUT_PULLUP);
} //end constructor

int Ultrasonic::measure() {
    // Make sure that trigger pin is LOW.
    digitalWrite(triggerPin, LOW);
    // Hold trigger for 10 microseconds, which is signal for sensor to measure distance.
    digitalWrite(triggerPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(triggerPin, LOW);
    delayMicroseconds(10);
    // Measure the length of echo signal, which is equal to the time needed for sound to go there and back.
    int distanceCm = pulseIn(echoPin, HIGH, MAX_WAIT);
    distanceCm = distanceCm/58; // (2.0/0.0343);
    if ((distanceCm == 0)||(distanceCm > MAX_DISTANCE)) { // maximum distance is 150cm --> 1.5m 
        //return distanceCm;
        return 999; // too far away
    } else { // good data
        return distanceCm;
    }
    delay(50); //delay for 50ms to ensure the ultrasonic "beep" has faded away and will not cause a false echo on the next ranging
}// end measure

#endif //__ULTRASONIC_CPP
