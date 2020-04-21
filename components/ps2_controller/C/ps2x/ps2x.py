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
from streamReader import StreamReader
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
        self.TARGET = './ps2x'

        self.ps2obj = sp.Popen([self.TARGET,
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
        self.data = str()
        self.li = list()
        self.li_len = 0
        print('PS2 Controller ready!')

    def __del__(self):
        """
        Destructor
        """
        self.clean()
    
    def changed(self):
        output = self.output.readline(0.05)  # 0.05 secs = 50ms to let the shell output the result
        error  = self.error.readline(0.05)  # 0.05 secs = 50ms to let the shell output the result
        sys.stdout.flush()
        if error is not None:
            raise ValueError(error.strip().decode("utf-8"))
        if output is not None:  # turn it into string if it is not a null
            self.data = output.strip().decode("utf-8")
            self.li = list(self.data.split(" "))
            self.li_len = len(self.li)
            if self.li_len > 3: # if this is information, then dump it to output
                print(self.data)
                return False
            return True
        else:
            return False

    def read(self):
        if self.li_len != 3:
            return self.data
        else:
            return None

    def readStick(self):
        if self.li_len is 3: # if the collected frame is correct
            return self.li
        else: # if it is not the analog sticks
            return [None, 0, 0]
        
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
