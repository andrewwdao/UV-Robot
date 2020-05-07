/*------------------------------------------------------------*-
  Library for controlling PS2X controller with Raspberry Pi
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020  <bit.ly/DMA-HomePage> <minhan7497@gmail.com>.
  version 1.00 - 19/04/2020
 --------------------------------------------------------------
 * Module created for the purpose of communicate 
 * with the PS2X controller.
 *
 * Tested with Ultrasonic sensor such as: HCSR04, HCSR05
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
#ifndef __ULTRASONIC_H
#define __ULTRASONIC_H
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <errno.h>
#include <wiringPi.h>


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
    double measure();

 private:
    int triggerPin, echoPin;
};

#endif // __HCSR04_H