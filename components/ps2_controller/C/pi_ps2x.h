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
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <errno.h>
#include <wiringPi.h>
#include <wiringPiSPI.h>

// ------ Public constants ------------------------------------
typedef unsigned char byte;
// typedef uint8_t bool
// ------ Public function prototypes --------------------------

// ------ Public variable -------------------------------------

//--------------------------------------------------------------
// CLASS DEFINITIONS
//--------------------------------------------------------------
class PS2X {
  public:
    PS2X(int, int, bool, bool, bool); // constructor
    ~PS2X();                // destructor
    // bool reconfig(bool, bool, bool); // reconfig the controller
    // void update(void); // very important function to put in the loop


    
  private:
    void __shiftout(byte*); // performs a simultaneous write/read transaction over the selected SPI bus

    byte spi_channel;
    int spi_speed;
    bool en_analog;
    bool en_pressure;
    bool en_rumble;
    byte message[21] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    static int myspi;

};
#endif //__PI_PS2X_H