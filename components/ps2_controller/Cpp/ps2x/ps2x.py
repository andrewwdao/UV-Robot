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
 --------------------------------------------------------------"""
import subprocess as sp
from ps2x.streamReader import StreamReader
import sys
import time

PS2_DAT = 13  # wiringPi pin (not BCM). ref: http://wiringpi.com/pins/
PS2_CMD = 12  # wiringPi pin (not BCM). ref: http://wiringpi.com/pins/
PS2_SEL = 10  # wiringPi pin (not BCM). ref: http://wiringpi.com/pins/
PS2_CLK = 14  # wiringPi pin (not BCM). ref: http://wiringpi.com/pins/
PS2_ANALOG   = True
PS2_LOCKED   = True
PS2_PRESSURE = False
PS2_RUMBLE   = False

class PS2X(object):
    """
    A python written module for interacting with the PS2X controller.

    """
    def __init__(self, dat = PS2_DAT,
                       cmd = PS2_CMD,
                       sel = PS2_SEL,
                       clk = PS2_CLK,
                       analog = PS2_ANALOG,
                       locked = PS2_LOCKED,
                       press = PS2_PRESSURE,
                       rumble = PS2_RUMBLE):
        """
        Constructor
        @param dat: an integer indicates the data pin of the PS2
        @param cmd: an integer indicates the command pin of the PS2
        @param sel: an integer indicates the select pin of the PS2
        @param clk: an integer indicates the clock pin of the PS2
        @param en_analog: a boolean indicates the analog mode of the PS2
        @param en_locked: aa boolean indicates the lock or unlock mode of the PS2
        @param en_pressures: a boolean indicates the pressure function of the PS2
        @param en_rumble: aa boolean indicates the rumble of the PS2
        """
        self.dat_pin = dat
        self.cmd_pin = cmd
        self.sel_pin = sel
        self.clk_pin = clk
        self.en_analog = analog
        self.en_locked = locked
        self.en_pressures = press
        self.en_rumble = rumble

        # DualShock button constants
        self.SELECT     = 0x0001
        self.L3         = 0x0002
        self.R3         = 0x0004
        self.START      = 0x0008
        self.UP         = 0x0010
        self.RIGHT      = 0x0020
        self.DOWN       = 0x0040
        self.LEFT       = 0x0080
        self.L2         = 0x0100
        self.R2         = 0x0200
        self.L1         = 0x0400
        self.R1         = 0x0800
        self.TRIANGLE   = 0x1000
        self.CIRCLE     = 0x2000
        self.CROSS      = 0x4000
        self.SQUARE     = 0x8000

        # self.TARGET = './ps2x'
        self.TARGET = '/home/pi/system/components/ps2_controller/Cpp/ps2x/ps2x'
        self.ps2obj = sp.Popen(['sudo',self.TARGET,
                                       '-d', str(self.dat_pin),
                                       '-c', str(self.cmd_pin),
                                       '-s', str(self.sel_pin),
                                       '-k', str(self.clk_pin),
                                       '-a', str(self.en_analog),
                                       '-l', str(self.en_locked),
                                       '-p', str(self.en_pressures),
                                       '-r', str(self.en_rumble)],
                                       shell=False,
                                       stdout=sp.PIPE,
                                       stderr=sp.PIPE)
        self.output  = StreamReader(self.ps2obj.stdout)
        self.error   = StreamReader(self.ps2obj.stderr) 
        self.buttons = 0
        self.last_buttons = 0
        self.Lsticks = 0
        self.last_Lsticks = 0

        print('PS2 Controller Ready!')


    def __del__(self):
        """
        Destructor
        """
        self.clean()
    
    def update(self):
        output = self.output.readline(0.05)  # 0.05 secs = 50ms to let the shell output the result
        error  = self.error.readline(0.05)  # 0.05 secs = 50ms to let the shell output the result
        sys.stdout.flush()
        if error is not None:
            raise ValueError(error.strip().decode("utf-8"))
        if output is not None:  # turn it into string if it is not a null
            raw_data = output.strip().decode("utf-8")
            data = list(raw_data.split(" "))
            if (len(data) is 3) and (data[0] == "Data:"): # correct frame
                    self.last_buttons = self.buttons
                    self.last_Lsticks = self.Lsticks
                    self.buttons = int(data[1])
                    self.Lsticks = int(data[2])
            else: # if this is information, then dump it to output
                print(raw_data)

    def buttonChanged(self): # will be TRUE if any button changes state (on to off, or off to on)
        return (self.last_buttons^self.buttons)>0
    
    def LstickChanged(self): # will be TRUE if Left stick changed
        return (self.last_Lsticks^self.Lsticks)>0
    
    def changed(self): # will be TRUE if any button changes state (on to off, or off to on) or Left stick changed
        return self.buttonChanged()|self.LstickChanged()

    def isPressing(self, button): # will be TRUE as long as button is pressed
        return (~self.buttons & button)>0

    def pressed(self, button): # will be true only once when button is pressed
        return self.buttonChanged() & self.isPressing(button)
    
    def released(self, button): # will be true only once when button is released
        return self.buttonChanged() & ((~self.last_buttons & button) > 0)
    
    def LstickRead(self): # release adc value of the Left analog stick
        LX = self.Lsticks >> 8
        LY = self.Lsticks & 0x0F
        return [LX,LY]
        
    def flush(self):
        sys.stdout.flush() # flush all the left over from buffer
        return

    def clean(self):
        # check if process terminated or not
        # A None value indicates that the process hasn't terminated yet.
        if self.ps2obj.poll() is None:
            self.ps2obj.terminate()
            self.ps2obj.kill()
            print('PS2 Controller terminated!')
