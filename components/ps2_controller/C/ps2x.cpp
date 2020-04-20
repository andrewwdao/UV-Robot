/*------------------------------------------------------------*-
  RFID reader main functions file
  Tested with Gwiot 7304D2 RFID Reader(26 bit Wiegand mode) and RASPBERRY PI 3B+
    (c) Minh-An Dao 2019
    (c) Spiros Ioannou 2017
  version 1.10 - 25/10/2019
 --------------------------------------------------------------
 *
 * Usage:
 * ./rfid_main [-d] [-h] [-a] [-0 D0-pin] [-1 D1-pin]
 *  With:
 *  -d : debug mode
 *  -h : help
 *  -a : dumb all received information out
 *  -0 D0-pin: GPIO pin for data0 pulse (wiringPi pin)
 *  -1 D1-pin: GPIO pin for data1 pulse (wiringPi pin)
 *
 -------------------------------------------------------------- */
#include <time.h>
#include <unistd.h>
#include <memory.h>
#include <sys/time.h>
#include <signal.h>
#include "pi_ps2x.h"

// --- Defaults, change with command-line options
#define SPI_CHANNEL 0
#define SPI_SPEED 500000

#define PS2_DAT 13  // wiringPi
#define PS2_CMD 12 // wiringPi
#define PS2_SEL 10  // wiringPi
#define PS2_CLK 14 // wiringPi
#define PS2_ANALOG true
#define PS2_LOCKED true
#define PS2_PRESSURE false
#define PS2_RUMBLE false

struct option_s {
    int spi_channel;
    int spi_speed;
	//char debug;
} options;

int main(int argc, char *argv[]) {
    /* defaults */
    options.spi_channel = SPI_CHANNEL;
    options.spi_speed = SPI_SPEED;
    //options.debug = 0;
    //options.in_system = 1;

    /* Parse Options */
    int opt;
    while ((opt = getopt(argc, argv, "dhc:s:")) != -1) {
        switch (opt) {
        case 'd': //debug
            //options.debug++;
            break;
        case 'h':
            //rfid_showUsage();
            exit(0);
            break;
        case 'c': //channel
            options.spi_channel = atoi(optarg);
            break;
        case 's':
            options.spi_speed = atoi(optarg);
            break;
        default: /* unknown command */
            //rfid_showUsage();
            exit(0);
        }//end switch case
    }//end while

    PS2X ps2(PS2_DAT, PS2_CMD,PS2_SEL, PS2_CLK,PS2_ANALOG,PS2_LOCKED,PS2_PRESSURE,PS2_RUMBLE); //options.spi_channel,
    //          options.spi_speed,
	// 		 0,0,0
    //           //options.debug,
    //         );

    while (1) {
        ps2.update();
        if (ps2.pressed(CROSS)) {printf("Cross pressed\n");}
        if {ps2.isPressing(DOWN)} {printf("Down is being pressed\n")}
        //pause(); //pause to wait for ISR and not consuming system memory
    }//end while
}//end main

