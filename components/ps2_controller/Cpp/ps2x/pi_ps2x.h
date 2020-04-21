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
#ifndef __PI_PS2X_H
#define __PI_PS2X_H
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <errno.h>
#include <wiringPi.h>

// ------ Public constants ------------------------------------
typedef unsigned char byte;

// --- DualShock button bit
#define SELECT     0x0001
#define L3         0x0002
#define R3         0x0004
#define START      0x0008
#define UP         0x0010
#define RIGHT      0x0020
#define DOWN       0x0040
#define LEFT       0x0080
#define L2         0x0100
#define R2         0x0200
#define L1         0x0400
#define R1         0x0800
#define TRIANGLE   0x1000
#define CIRCLE     0x2000
#define CROSS      0x4000
#define SQUARE     0x8000

// Analog Stick address
#define RX  5
#define RY  6
#define LX  7
#define LY  8
// ------ Public function prototypes --------------------------

// ------ Public variable -------------------------------------

//--------------------------------------------------------------
// CLASS DEFINITIONS
//--------------------------------------------------------------
class PS2X {
  public:
    PS2X(int,int,int,int,bool,bool,bool,bool); // constructor
    ~PS2X();                                   // destructor
    void changeMode(bool, bool);               // change analog-digital, lock-unlock. CAUTION: must call reconfig to update the changes
    void changeMode(bool, bool,bool,bool);     // change analog-digital, lock-unlock, pressure and rumble mode. CAUTION: must call reconfig to update the changes
    void reconfig(void);                       // reconfig the controller. MUST be called after any changMode
    void update(void);                         // very important function to put in the loop

    bool buttonChanged(void);                  // will be TRUE if any button was changed
    bool LstickChanged(void);                  // will be TRUE if Left stick was changed. You can add another one for Right one if you like
    bool changed(void);                        // will be TRUE if anybutton or stick was changed
    bool isPressing(int);                      // will be TRUE as long as a selected button was being pressed
    bool pressed(int);                         // will be TRUE once after a selected button was pressed
    bool released(int);                        // will be TRUE once after a selected button was released
    int rawButton(void);                       // return raw button value for python module
    int rawLastButton(void);                   // return last raw button value for python module
    int rawLStick(void);                       // return raw Lstick adc value for python module
    int rawLastLStick(void);                       // return last raw Lstick adc value for python module
    int readAnalog(int);                       /* return analog value (byte) of the selected button (or stick)
                                               // WARNING: there are no analog value for SELECT, START, L3, R3 buttons.
                                                           Please don't try put them in this function, otherwise result may not be what you're looking for*/
    
  private:
    byte __shiftout(byte);                     // performs a simultaneous write/read transaction over the selected bus
    int __sendCommand(byte*,int);              // only send command and return the status of the sending, not receive anything
    int __getData(byte*,int);                  // send command and get the corresponding response from controller (save in this->ps2data)

    int dat;
    int cmd;
    int sel;
    int clk;
    bool en_analog;
    bool en_locked;
    bool en_pressure;
    bool en_rumble;
    unsigned long last_millis;
    int last_buttons;
    int buttons;
    int last_Lsticks;
    int Lsticks;
    byte ps2data[21] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}; // maximum dataframe

};
#endif //__PI_PS2X_H