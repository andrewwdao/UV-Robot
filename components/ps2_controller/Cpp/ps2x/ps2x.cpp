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
#include "pi_ps2x.h"

// --- Defaults, change with command-line options
#define PS2_DAT 13  // wiringPi
#define PS2_CMD 12 // wiringPi
#define PS2_SEL 10  // wiringPi
#define PS2_CLK 14 // wiringPi
#define PS2_ANALOG false
#define PS2_LOCKED false
#define PS2_PRESSURE false
#define PS2_RUMBLE false

struct option_s {
    int ps2_dat;
    int ps2_cmd;
    int ps2_sel;
    int ps2_clk;
    bool ps2_analog;
    bool ps2_locked;
    bool ps2_pressure;
    bool ps2_rumble;
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

void sendData(int dat1, int dat2)
{
    fprintf(stdout, "Data: %d %d\n", dat1, dat2);
    fflush(stdout);
}

int main(int argc, char *argv[]) {
    /* defaults */
    options.ps2_dat = PS2_DAT;
    options.ps2_cmd = PS2_CMD;
    options.ps2_sel = PS2_SEL;
    options.ps2_clk = PS2_CLK;
    options.ps2_analog = PS2_ANALOG;
    options.ps2_locked = PS2_LOCKED;
    options.ps2_pressure = PS2_PRESSURE;
    options.ps2_rumble = PS2_RUMBLE;

    /* Parse Options */
    int opt;
    while ((opt = getopt(argc, argv, "hd:c:s:k:a:l:p:r:")) != -1) {
        switch (opt) {
        case 'h':
            showUsage();
            break;
        case 'd': //set new data pin
            options.ps2_dat = atoi(optarg);
            break;
        case 'c': //set new command pin
            options.ps2_cmd = atoi(optarg);
            break;
        case 's': //set new select pin
            options.ps2_sel = atoi(optarg);
            break;
        case 'k': //set new clock pin
            options.ps2_clk = atoi(optarg);
            break;
        case 'a': //turn on or off analog mode
            options.ps2_analog = atoi(optarg);
            break;
        case 'l': //turn on or off locked mode
            options.ps2_locked = atoi(optarg);
            break;
        case 'p': //turn on or off pressure mode
            options.ps2_pressure = atoi(optarg);
            break;
        case 'r': //turn on or off rumble mode
            options.ps2_rumble = atoi(optarg);
            break;
        default: /* unknown command */
            showUsage(); exit(0);
            break;
        }//end switch case
    }//end while

    /*declare our main object*/
    PS2X ps2(options.ps2_dat,
             options.ps2_cmd,
             options.ps2_sel,
             options.ps2_clk,
             options.ps2_analog,
             options.ps2_locked,
             options.ps2_pressure,
             options.ps2_rumble
            );

    /*now come the loop*/
    bool changed_flag = false;
    while (1) {
        ps2.update();
        if (ps2.changed()) 
        {   
            changed_flag = true;
            sendData(ps2.rawButton(), ps2.rawLStick());
        }
        else if (changed_flag) //need to have this to main system to compare
        {
            changed_flag = false;
            sendData(ps2.rawButton(), ps2.rawLStick());
        }

        //pause(); //pause to wait for ISR and not consuming system memory

    }//end while
}//end main
