/*------------------------------------------------------------*-
  Main execution code for controlling PS2X controller with Raspberry Pi
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
#include <time.h>
#include <unistd.h>
#include <memory.h>
#include <sys/time.h>
#include <signal.h>
#include "pi_ultrasonic.h"

// --- Defaults, change with command-line options
#define TRIG_PIN 0 // wiringPi
#define ECHO_PIN 2 // wiringPi

struct option_s {
    int trig_pin;
    int echo_pin;
} options;

void showUsage(void) {
    printf("\n\n---------PS2 library for Raspberry Pi---------\n\n");
    printf("Usage: (run as root)\n");
    printf("./ps2x [-h] [-d DATA-pin] [-c CMD-pin] [-s SELECT-pin] [-k CLOCK-pin] [-a ANALOG] [-l LOCK] [-p PRESS] [-r RUMBLE]\n");
    printf("With:\n");
    printf("\t-h            : show help\n");
    printf("\t-d DATA-pin   : GPIO pin for data pin (wiringPi pin)\n");
    printf("\t-c CMD-pin    : GPIO pin for command pin (wiringPi pin)\n");
    printf("\t-s SELECT-pin : GPIO pin for select pin (wiringPi pin)\n");
    printf("\t-k CLOCK-pin  : GPIO pin for data pin (wiringPi pin)\n");
    printf("\t-a ANALOG     : turn on or off analog mode (1 to turn on, 0 to turn off)\n");
    printf("\t-l LOCK       : turn on or off lock mode (1 to turn on, 0 to turn off)\n");
    printf("\t-p PRESS      : turn on or off pressure mode (1 to turn on, 0 to turn off)\n");
    printf("\t-r RUMBLE     : turn on or off rumble mode (1 to turn on, 0 to turn off)\n\n");
    printf("Example: * Run as default:  sudo ./ps2x\n");
    printf("         * Change pins:     sudo ./ps2x -d 9 -c 10 -s 8 -k 11\n");
    printf("         * Change modes:    sudo ./ps2x -a 1 -l 1 -p 0 -r 1\n\n");
    printf("(c) Minh-An Dao 2020  <bit.ly/DMA-HomePage> <minhan7497@gmail.com>.\n");
    exit(0);
}//end showUsage

int main(int argc, char *argv[]) {
    /* defaults */
    options.trig_pin = TRIG_PIN;
    options.echo_pin = ECHO_PIN;
    

    /* Parse Options */
    int opt;
    while ((opt = getopt(argc, argv, "ht:e:")) != -1) {
        switch (opt) {
        case 'h':
            showUsage();
            break;
        case 't': //set new trigger pin
            options.trig_pin = atoi(optarg);
            break;
        case 'e': //set new command pin
            options.echo_pin = atoi(optarg);
            break;
        default: /* unknown command */
            showUsage(); exit(0);
            break;
        }//end switch case
    }//end while

    /*declare our main object*/
    Ultrasonic ultrasonic(options.trig_pin,
               options.echo_pin
               );

    /*now come the loop*/
    // bool changed_flag = false;
    while (1) {
        double distance = ultrasonic.measure();
        if (distance != -1.0) {
            fprintf(stdout, "Distance: %02f\n", distance);
            fflush(stdout);
        }

        //pause(); //pause to wait for ISR and not consuming system memory

    }//end while
}//end main
