/*------------------------------------------------------------*-
  Library for controlling PS2X controller with Raspberry Pi
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020  <bit.ly/DMA-HomePage> <minhan7497@gmail.com>.
  version 1.00 - 19/04/2020
 --------------------------------------------------------------
 * Module created for the purpose of communicate 
 * with the PS2X controller.
 *
 * Ported from Arduino-PS2X library (https://github.com/madsci1016/Arduino-PS2X)
 * Documents:
 *  - https://store.curiousinventor.com/guides/PS2
 *  - https://gist.github.com/scanlime/5042071
 * 
 * Check out wiringPi pins, they are different from BCM pins (http://wiringpi.com/pins/)
 * ------ Pinout (wiringPi pins) ------
 * 13 - MISO  -  data (controller > pi)
 * 12 - MOSI  -  command (pi > controller)
 * 14 - SCLK  -  Clock
 * 10 - CE0   -  Attention (CS) (slave select)
 * 
 * All mode:
        0x41: Digital mode with ONE 16 bit words (2 bytes) follow the header.
                Contains only digital states of the buttons (byte 4 and byte 5)
        
        0x73: Analog mode with THREE 16 bit words (6 bytes) follow the header.
                Contain digital states of the buttons (byte 4 + byte 5)
                Contain 02 joystick ADC values:
                - Right Joystick (byte 6 + byte 7)
                - Left Joystick (byte 8 + byte 9)
        0x79: Analog mode with NINE 16 bit words (18 bytes) follow the header.
                Contain digital states of the buttons (byte 4 + byte 5)
                Contain 02 joystick ADC values:
                - Right Joystick (byte 6 + byte 7)
                - Left Joystick (byte 8 + byte 9)
                Contain adc value of 12 Button (pressures) (from byte 10 to byte 21) 
        
        0xFx: Config mode
 *
 * 
 * Usage: (root)
 * ./ps2x [-h] [-d DATA-pin] [-c CMD-pin] [-s SELECT-pin] [-k CLOCK-pin] [-a ANALOG] [-l LOCK] [-p PRESS] [-r RUMBLE] 
 *  With:
 *  -h            : show help
 *  -d DATA-pin   : GPIO pin for data pin (wiringPi pin)
 *  -c CMD-pin    : GPIO pin for command pin (wiringPi pin)
 *  -s SELECT-pin : GPIO pin for select pin (wiringPi pin)
 *  -k CLOCK-pin  : GPIO pin for data pin (wiringPi pin)
 *  -a ANALOG     : turn on or off analog mode (1 to turn on, 0 to turn off)
 *  -l LOCK       : turn on or off lock mode (1 to turn on, 0 to turn off)
 *  -p PRESS      : turn on or off pressure mode (1 to turn on, 0 to turn off)
 *  -r RUMBLE     : turn on or off rumble mode (1 to turn on, 0 to turn off)
 * 
 * Example: * Run as default:  sudo ./ps2x
 *          * Change pins:     sudo ./ps2x -d 9 -c 10 -s 8 -k 11
 *          * Change modes:    sudo ./ps2x -a 1 -l 1 -p 0 -r 1
 *
 * 
 * Licensed under the MIT license. All right reserved.
 --------------------------------------------------------------*/
#ifndef __ULTRASONIC_CPP
#define __ULTRASONIC_CPP
#include "pi_ultrasonic.h"


// ------ Private constants -----------------------------------
// --- Defaults, change with command-line options
#define TRIG_PIN 0 // wiringPi
#define ECHO_PIN 2 // wiringPi

#define MAX_DISTANCE 25 //cm
const double TIMEOUT = 1500;  // us, calculate base on distanceCm =  durationMicroSec / 2.0 * 0.0343
// ------ Private function prototypes -------------------------

// ------ Private variables -----------------------------------

// ------ PUBLIC variable definitions -------------------------

//--------------------------------------------------------------
// FUNCTION DEFINITIONS
//--------------------------------------------------------------
Ultrasonic::Ultrasonic(int triggerPin = TRIG_PIN,
                       int echoPin = ECHO_PIN) {
    this->triggerPin = triggerPin;
    this->echoPin = echoPin;
    //---------------------- Setup wiringPi -----------------------
    wiringPiSetup();
    pinMode(this->triggerPin, OUTPUT);
    pinMode(this->echoPin, INPUT); pullUpDnControl(this->echoPin, PUD_DOWN);
} //end constructor

double Ultrasonic::measure() {
    // Make sure that trigger pin is LOW.
    digitalWrite(this->triggerPin, LOW);
    delayMicroseconds(2);
    // Hold trigger for 10 microseconds, which is signal for sensor to measure distance.
    digitalWrite(this->triggerPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(this->triggerPin, LOW);
    // wait for signal to go low
    while (!digitalRead(this->echoPin)) {delay(0);};
    // Measure the length of echo signal, which is equal to the time needed for sound to go there and back.
    unsigned long last_millis = micros(); // returns an unsigned 32-bit number which wraps after approximately 71 minutes.
    while (1) {
        delayMicroseconds(300);
        if (!digitalRead(this->echoPin)) {
            return ((float)(micros() - last_millis)/2.0*0.0343); // distance in Cm
        }//end if
        if ((micros() - last_millis)>TIMEOUT) {
            return -1.0; //too far away
        }
    }//end while
} //end measure

#endif //__PI_PS2X_CPP
