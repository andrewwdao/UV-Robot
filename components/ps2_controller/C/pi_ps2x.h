/*------------------------------------------------------------*-
  Library for controlling PS2X controller with Raspberry Pi
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020  <bit.ly/DMA-HomePage>.
  version 1.00 - 19/04/2020
 --------------------------------------------------------------
 * Module created for the purpose of communicate 
 * with the PS2X controller.
 *
 * Ported from Arduino-PS2X library (https://github.com/madsci1016/Arduino-PS2X)
 * Documents:
 *  - https://store.curiousinventor.com/guides/PS2
 *  - https://gist.github.com/scanlime/5042071
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
// ------ Public function prototypes --------------------------

// ------ Public variable -------------------------------------

//--------------------------------------------------------------
// CLASS DEFINITIONS
//--------------------------------------------------------------
class PS2X {
  public:
    PS2X(int,int,int,int,bool,bool,bool,bool); // constructor
    ~PS2X();                                   // destructor
    void changeMode(bool, bool); //change analog-digital, lock-unlock. CAUTION: must call reconfig to update the changes
    void changeMode(bool, bool,bool,bool); //change analog-digital, lock-unlock, pressure and rumble mode. CAUTION: must call reconfig to update the changes
    void reconfig(void); // reconfig the controller
    void update(void); // very important function to put in the loop

    bool changed(void); //will be TRUE if any button was changed
    bool isPressing(int); //will be TRUE as long as a selected button was being pressed
    bool pressed(int); //will be TRUE once after a selected button was pressed
    bool released(int); //will be TRUE once after a selected button was released
    int readAnalog(int); //return analog value (byte) of the selected button (or stick)
    
  private:
    byte __shiftout(byte); // performs a simultaneous write/read transaction over the selected bus
    int __sendCommand(byte*,int); // only send command and return the status of the sending, not receive anything
    int __getData(byte*,int); // send command and get the corresponding response from controller (save in this->ps2data)

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
    byte ps2data[21] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};

};
#endif //__PI_PS2X_H