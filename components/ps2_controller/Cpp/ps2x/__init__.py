"""------------------------------------------------------------*-
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
 * Licensed under the MIT license. All right reserved.
 --------------------------------------------------------------"""
from ps2x.ps2x import PS2X

PS2_DAT = 13  # wiringPi pin (not BCM). ref: http://wiringpi.com/pins/
PS2_CMD = 12  # wiringPi pin (not BCM). ref: http://wiringpi.com/pins/
PS2_SEL = 10  # wiringPi pin (not BCM). ref: http://wiringpi.com/pins/
PS2_CLK = 14  # wiringPi pin (not BCM). ref: http://wiringpi.com/pins/
PS2_ANALOG   = True
PS2_LOCKED   = True
PS2_PRESSURE = False
PS2_RUMBLE   = False

ps2 = PS2X(PS2_DAT, PS2_CMD, PS2_SEL, PS2_CLK, PS2_ANALOG, PS2_LOCKED, PS2_PRESSURE, PS2_RUMBLE)


