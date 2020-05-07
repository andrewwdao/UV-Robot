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

        # value for the buttons and sticks
        self.buttons = 0xFFFF # all button released
        self.last_buttons = 0xFFFF # all button released
        self.Lsticks = 0x807F # 128 << 8 + 127 --> stable state of the analog stick
        self.last_Lsticks = 0x807F # 128 << 8 + 127 --> stable state of the analog stick

        # self.TARGET = './ps2x'
        self.TARGET = '/ps2x/ps2x' # absolute directory, must run ps2_bin_reset.sh before run this
        try:
            self.ps2obj = sp.Popen(['sudo',self.TARGET,
                                        '-d', str(self.dat_pin),
                                        '-c', str(self.cmd_pin),
                                        '-s', str(self.sel_pin),
                                        '-k', str(self.clk_pin),
                                        '-a', str(int(self.en_analog)),
                                        '-l', str(int(self.en_locked)),
                                        '-p', str(int(self.en_pressures)),
                                        '-r', str(int(self.en_rumble))],
                                        shell=False,
                                        stdout=sp.PIPE,
                                        stderr=sp.PIPE)
        except Exception as e:
            print(e)
            raise ValueError("This may happened because you forgot to run ps2_bin_reset.sh. Please make sure to do that!")
        
        self.output  = StreamReader(self.ps2obj.stdout)
        self.error   = StreamReader(self.ps2obj.stderr) 

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
        return self.last_buttons != self.buttons
    
    def LstickChanged(self): # will be TRUE if Left stick changed
        return self.last_Lsticks != self.Lsticks
    
    def changed(self): # will be TRUE if any button changes state (on to off, or off to on) or Left stick changed
        return self.buttonChanged()|self.LstickChanged()
    
    def pressed(self, button): # will be true only once when button is pressed
        return self.buttonChanged() & self.isPressing(button)

    # released must be place independently, not hybrid under a pressing method!  
    def released(self, button): # will be true only once when button is released
        return self.buttonChanged() & ((~self.last_buttons & button) > 0)
    
    def buttonPressing(self): # will be TRUE as long as ANY button is pressed
        return ~self.buttons
    
    def arrowPressing(self): # will be TRUE as long as arrow buttons (UP, DOWN, RIGHT, LEFT) are pressed
        return (~self.buttons & 0x00F0)>0  # 0x00F0 = 0b0000000011110000 --> location of the arrow bits

    def LRpressing(self): # will be TRUE as long as LR buttons (L1, L2, L3, R1, R2, R3) are pressed
        return (~self.buttons & 0x0F06)>0  # 0x0F06 = 0b0000111100000110 --> location of the LR bits
    
    def cmdPressing(self): # will be TRUE as long as Command buttons (Cross, square, circle, triangle, select, start) are pressed
        return (~self.buttons & 0xF009)>0  # 0xF009 = 0b1111000000001001 --> location of the command bits

    def isPressing(self, button): # will be TRUE as long as a specific button is pressed
        return (~self.buttons & button)>0

    def LstickTouched(self): # will triggered when Left stick is out of stable position (may not changing though)
        return self.Lsticks != 0x807F # ps2.LstickRead() != [128, 127]

    def LstickRead(self): # release adc value of the Left analog stick
        LX = self.Lsticks >> 8
        LY = self.Lsticks & 0x00FF
        return [LX,LY]
    
    def LxRead(self):
        return self.Lsticks >> 8
    
    def LyRead(self):
        return self.Lsticks & 0x00FF

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
