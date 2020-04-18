"""------------------------------------------------------------*-
  Main module for PS2X controller
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020
  version 1.00 - 17/04/2020
 --------------------------------------------------------------
 * Module created for the purpose of receiving signal 
 * from the PS2X controller.
 *
 * Ported from Arduino-PS2X library (https://github.com/madsci1016/Arduino-PS2X)
 --------------------------------------------------------------"""
import RPi.GPIO as GPIO
from datetime import datetime
import time

PS2_DAT = 4  # BCM mode
PS2_CMD = 17 # BCM mode
PS2_SEL = 27 # BCM mode
PS2_CLK = 22 # BCM mode

CTRL_BYTE_DELAY = 0.000005 # 18us
CTRL_CLK = 0.000005 # 5us
UPDATE_INTERVAL = 70000.0 # us --> 50ms, must set .0 to make it a float
EXPIRED_INTERVAL = 1500000 # us --> 1,5s

enter_config = (0x01,0x43,0x00,0x01,0x00)
set_mode_analog = (0x01,0x44,0x00,0x01,0x03,0x00,0x00,0x00,0x00)
# Controller defaults to digital mode and only transmits the on / off status of the buttons in the 4th and 5th byte.
# No joystick data, pressure or vibration control capabilities.
set_mode_digital = (0x01,0x44,0x00,0x00,0x03,0x00,0x00,0x00,0x00)
set_bytes_large = (0x01,0x4F,0x00,0xFF,0xFF,0x03,0x00,0x00,0x00)
exit_config = (0x01,0x43,0x00,0x00,0x5A,0x5A,0x5A,0x5A,0x5A)
enable_rumble = (0x01,0x4D,0x00,0x00,0x01)
type_read = (0x01,0x45,0x00,0x5A,0x5A,0x5A,0x5A,0x5A,0x5A)

# DualShock analog slot number
analogSlot = {
         5 : 5,
         6 : 6,
         7 : 7,
         8 : 8,
    0x0010 : 11, # UP
    0x0020 : 9,  # RIGHT
    0x0040 : 12, # DOWN
    0x0080 : 10, # LEFT
    0x0100 : 19, # L2
    0x0200 : 20, # R2
    0x0400 : 17, # L1
    0x0800 : 18, # R1
    0x1000 : 13, # TRIANGLE - GREEN
    0x2000 : 14, # CIRCLE - RED
    0x4000 : 15, # CROSS - BLUE
    0x8000 : 16  # SQUARE - PINK
}

class PS2X(object):
    """
    A python written library for the PS2X controller.

    """

    def __init__(self, dat = PS2_DAT, cmd = PS2_CMD, sel = PS2_SEL, clk = PS2_CLK, press = False, rumble = False):
        """
        Constructor
        @param dat: an integer indicates the data pin of the PS2
        @param cmd: an integer indicates the command pin of the PS2
        @param sel: an integer indicates the select pin of the PS2
        @param clk: an integer indicates the clock pin of the PS2
        @param en_Pressures: a boolean indicates the pressure function of the PS2
        @param en_Rumble: aa boolean indicates the rumble of the PS2
        """
        self.dat = dat
        self.cmd = cmd
        self.sel = sel
        self.clk = clk
        self.en_Pressures = press
        self.en_Rumble = rumble     

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dat, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.cmd, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.sel, GPIO.OUT)
        GPIO.setup(self.clk, GPIO.OUT, initial=GPIO.HIGH)
        self.last_millis = datetime.now().microsecond
        self._ps2data = [0]*21 # full data frame
        self.last_buttons = 0
        self.buttons = 0

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

        # stick values
        self.R_STICK_X = 5
        self.R_STICK_Y = 6
        self.L_STICK_X = 7
        self.L_STICK_Y = 8
        
        # -----------(0x01,0x42,0,Motor1,Motor2,0,0,0,0)
        self.data_request = [0x01,0x42,0,False,0x00,0,0,0,0]

        watchdog = datetime.now().second
        while True:
            # read gamepad to see if it's talking
            self.__getData(self.data_request)
        
            print('Command 0x42: ', self._ps2data)
            '''
            All mode: self._ps2data[1]
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

            '''
            # check if valid mode came back.
            if [0x41,0x73,0x79,0xF1,0xF3,0xF9].count(self._ps2data[1]):
                break

            if (datetime.now().second - watchdog) > 1: # one second to connect, if not connected then raise error
                raise Exception("No controller found, please check wiring again.") # return error code 1 - Controller mode not matched or no controller found, expected 0x41, 0x42, 0x73 or 0x79
        
        # ------ entering config mode
        self.__sendCommand(enter_config) # start config run
        
        self.__getData(type_read)
        
        print('0x45: ', self._ps2data)
        if self._ps2data[0] == [0xFF] and
           self._ps2data[2] == [0x5A]: # if package header is correct [0xFF,0xF1-0xF3-0xF9,0x5A]
            controller_type = self._ps2data[3] # this is exactly what we want
        else: # package header is wrong
            controller_type = 0xFF # tell the system that something is wrong

        self.__sendCommand(set_mode_analog)
        if self.en_Rumble:
            self.__sendCommand(enable_rumble)
        if self.en_Pressures:
            self.__sendCommand(set_bytes_large)
        self.__sendCommand(exit_config)

        # ------- Done first config, now check response of the system
        self.__getData(self.data_request) # read to see if new data is comming

        if self.en_Pressures:
            if self._ps2data[1] == 0x79:
                print("Entered Pressures mode")
            if self._ps2data[1] == 0x73:
                print("Controller refusing to enter Pressures mode, may not support it.")

        if self._ps2data[1] != 0x79 and self._ps2data[1] != 0x73:
            print(self._ps2data)
            raise Exception("Controller found but not accepting commands.")

        print("Configured successful. Controller:")
        if controller_type == 0x03:
            print("DualShock")
        elif controller_type == 0x01 and self._ps2data[1] != 0x42:
            print("GuitarHero (Not supported yet)")
        elif controller_type == 0x0C:
            print("2.4G Wireless DualShock")
        elif controller_type == 0xFF:
            print("Wrong package header. Please check again")
        else:
            print("Unknown type")
        return # all good

    def __del__(self):
        """
        Destructor
        """
        ## Clean up GPIOs
        GPIO.cleanup()

    def __set(self, x, y): # need to set x = __set (x,y)
        return x|(1<<y)
    
    def __clr(self, x, y): # need to set x = __clr (x,y)
        return x&(~(1<<y))
    
    def __tog(self, x, y): # need to set x = __tog (x,y)
        return x^(1<<y)
    
    def __chk(self, x, y):
        return x&(1<<y)
    
    def __shiftinout(self, byte):
        received = 0 # received data default to be 0
        for i in range(0,8):
            if self.__chk(byte, i):
                GPIO.output(self.cmd, GPIO.HIGH) # CMD_SET
            else:
                GPIO.output(self.cmd, GPIO.LOW) # CMD_CLR
            
            GPIO.output(self.clk, GPIO.LOW) # CLK_CLR
            time.sleep(CTRL_CLK)

            if GPIO.input(self.dat) == GPIO.HIGH:
                received = self.__set(received, i)
            
            GPIO.output(self.clk, GPIO.HIGH) # CLK_SET
            time.sleep(CTRL_CLK)
        
        GPIO.output(self.cmd, GPIO.HIGH) # CMD_SET
        time.sleep(CTRL_BYTE_DELAY)
        return received
    
    def __sendCommand(self, command):
        GPIO.output(self.sel, GPIO.LOW)  # SEL_CLR - enable joystick
        time.sleep(CTRL_BYTE_DELAY)
        for y in range(0,len(command)):
            self.__shiftinout(command[y])
        GPIO.output(self.sel, GPIO.HIGH) # SEL_SET - disable joystick
        time.sleep(CTRL_BYTE_DELAY)

    def __reconfig(self):
        self.__sendCommand(enter_config)
        self.__sendCommand(set_mode_analog)
        if self.en_Rumble:
            self.__sendCommand(enable_rumble)
        if self.en_Pressures:
            self.__sendCommand(set_bytes_large)
        self.__sendCommand(exit_config)


    def __getData(self, command): # send command to ps2 and get response to the self._ps2data
        # get new data
        GPIO.output(self.cmd, GPIO.HIGH) # CMD_SET
        GPIO.output(self.clk, GPIO.HIGH) # CLK_SET
        GPIO.output(self.sel, GPIO.LOW)  # SEL_CLR - enable joystick
        time.sleep(CTRL_BYTE_DELAY)
    
        # Send the command to get button and joystick data
        for x in range(0,9):
            self._ps2data[x] = self.__shiftinout(command[x])

        # if controller is in full analog return mode
        # get the rest of the data
        if self._ps2data[1] == 0x79:
            for x in range(0,12):
                self._ps2data[x+9] = self.__shiftinout(0)
        
        GPIO.output(self.sel, GPIO.HIGH) # SEL_SET - disable joystick
        time.sleep(CTRL_BYTE_DELAY)

    def update(self):
        temp = datetime.now().microsecond - self.last_millis

        if temp > EXPIRED_INTERVAL: # us --> waited too long
            print("Waited too long. Try to reset...")
            self.__reconfig()

        if temp < UPDATE_INTERVAL: # us --> wait a little bit longer before read
            time.sleep(UPDATE_INTERVAL/1000000) # transfer to second, becareful, UPDATE_INTERVAL has to be float
        
        self.__getData(self.data_request)
        
        # Check to see if we received valid data or not.  
        # We should be in analog mode for our data to be valid (analog == 0x7_)
        if (self._ps2data[1] & 0xf0) != 0x70:
            print(self._ps2data[1])
            print("Not valid data received. Try to recover...")
            self._ps2data = [0]*21 # if not valid, then reset the whole frame
            # If we got here, we are not in analog mode, try to recover...
            time.sleep(0.07)
            self.__reconfig() # try to get back into Analog mode.
            return 
        
        # store the previous buttons states before get the new one
        self.last_buttons = self.buttons 

        # byte 4 and 5 of the data is the status of all buttons
        # store as one variable
        self.buttons = (self._ps2data[4] << 8) + self._ps2data[3]

        self.last_millis = datetime.now().microsecond
        return

    def changed(self): # will be TRUE if any button changes state (on to off, or off to on)
        return (self.last_buttons^self.buttons)>0

    def isPressing(self, button): # will be TRUE as long as button is pressed
        return (~self.buttons & button)>0

    def analogRead(self, button): # release adc value of an analog button
        return self._ps2data[analogSlot[button]]

    def pressed(self, button): # will be true only once when button is pressed
        return self.changed() & self.isPressing(button)
    
    def released(self, button): # will be true only once when button is released
        return self.changed() & ((~self.last_buttons & button) > 0)
    

    # def __init__(self, dat = PS2_DAT, cmd = PS2_CMD, sel = PS2_SEL, clk = PS2_CLK, press = False, rumble = False):
    #     """
    #     Constructor
    #     @param dat: an integer indicates the data pin of the PS2
    #     @param cmd: an integer indicates the command pin of the PS2
    #     @param sel: an integer indicates the select pin of the PS2
    #     @param clk: an integer indicates the clock pin of the PS2
    #     @param en_Pressures: a boolean indicates the pressure function of the PS2
    #     @param en_Rumble: aa boolean indicates the rumble of the PS2
    #     """
    #     self.dat = dat
    #     self.cmd = cmd
    #     self.sel = sel
    #     self.clk = clk
    #     self.en_Pressures = press
    #     self.en_Rumble = rumble     

    #     GPIO.setmode(GPIO.BCM)
    #     GPIO.setup(self.dat, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #     GPIO.setup(self.cmd, GPIO.OUT, initial=GPIO.HIGH)
    #     GPIO.setup(self.sel, GPIO.OUT)
    #     GPIO.setup(self.clk, GPIO.OUT, initial=GPIO.HIGH)
    #     self.last_millis = datetime.now().microsecond
    #     self.read_delay_s = 0.001 # 1ms
    #     self._ps2data = [0]*21
    #     self.last_buttons = 0
    #     self.buttons = 0
        
    #     # DualShock button constants
    #     self.SELECT     = 0x0001
    #     self.L3         = 0x0002
    #     self.R3         = 0x0004
    #     self.START      = 0x0008
    #     self.UP         = 0x0010
    #     self.RIGHT      = 0x0020
    #     self.DOWN       = 0x0040
    #     self.LEFT       = 0x0080
    #     self.L2         = 0x0100
    #     self.R2         = 0x0200
    #     self.L1         = 0x0400
    #     self.R1         = 0x0800
    #     self.TRIANGLE   = 0x1000
    #     self.CIRCLE     = 0x2000
    #     self.CROSS      = 0x4000
    #     self.SQUARE     = 0x8000

    #     # stick values
    #     self.R_STICK_X = 5
    #     self.R_STICK_Y = 6
    #     self.L_STICK_X = 7
    #     self.L_STICK_Y = 8
        
    #     # -----------(0x01,0x42,0,Motor1,Motor2,0,0,0,0)
    #     self.dword = [0x01,0x42,0,False,0x00,0,0,0,0]

    #     # read gamepad a few times to see if it's talking
    #     self.update()
    #     self.update()

    #     # see if mode came back. 
    #     # If still anything but 41, 73 or 79, then it's not talking
    #     if (self._ps2data[1] != 0x41 and
    #         self._ps2data[1] != 0x42 and
    #         self._ps2data[1] != 0x73 and
    #         self._ps2data[1] != 0x79): 
    #         raise Exception("No controller found, please check wiring again.") # return error code 1 - Controller mode not matched or no controller found, expected 0x41, 0x42, 0x73 or 0x79

    #     for y in range(0,11):
    #         self.__sendCommand(enter_config) # start config run

    #         # read controller type
    #         time.sleep(CTRL_BYTE_DELAY)
    #         GPIO.output(self.cmd, GPIO.HIGH) # CMD_SET
    #         GPIO.output(self.clk, GPIO.HIGH) # CLK_SET
    #         GPIO.output(self.sel, GPIO.LOW)  # SEL_CLR - enable joystick
    #         time.sleep(CTRL_BYTE_DELAY)

    #         temp = [0]*9
    #         for i in range(0,9):
    #             temp[i] = self.__shiftinout(type_read[i])

    #         GPIO.output(self.sel, GPIO.HIGH) # SEL_SET - disable joystick

    #         controller_type = temp[3]

    #         self.__sendCommand(set_mode)
    #         if self.en_Rumble:
    #             self.__sendCommand(enable_rumble)
    #         if self.en_Pressures:
    #             self.__sendCommand(set_bytes_large)
    #         self.__sendCommand(exit_config)

    #         self.update() # read to see if new data is comming

    #         if self.en_Pressures:
    #             if self._ps2data[1] == 0x79:
    #                 break
    #             if self._ps2data[1] == 0x73:
    #                 raise Exception("Controller refusing to enter Pressures mode, may not support it.")
            
    #         if self._ps2data[1] == 0x73:
    #             break

    #         if y is 10:
    #             raise Exception("Controller found but not accepting commands.")

    #         read_delay_s += 0.001 # add 1ms to read_delay_s

    #     print("Configured successful. Controller:")
    #     if controller_type == 0x03:
    #         print("DualShock")
    #     elif controller_type == 0x01 and self._ps2data[1] != 0x42:
    #         print("GuitarHero (Not supported yet)")
    #     elif controller_type == 0x0C:
    #         print("2.4G Wireless DualShock")
    #     else:
    #         print("Unknown")
    #     return # all good

    # def update(self):
    #     temp = datetime.now().microsecond - self.last_millis

    #     if temp > 1500000: # 1,5s -- waited too long
    #         self.__reconfig()

    #     if temp < self.read_delay_s*1000000: # converted to us, waited too short
    #         time.sleep(self.read_delay_s - float(float(temp)/1000000))
        
        
    #     # try a few times to get valid data...
    #     for i in range(0,5):
    #         GPIO.output(self.cmd, GPIO.HIGH) # CMD_SET
    #         GPIO.output(self.clk, GPIO.HIGH) # CLK_SET
    #         GPIO.output(self.sel, GPIO.LOW)  # SEL_CLR - enable joystick
    #         time.sleep(CTRL_BYTE_DELAY)
        
    #         # Send the command to get button and joystick data;
    #         for x in range(0,9):
    #             self._ps2data[x] = self.__shiftinout(self.command[x])

    #         # if controller is in full data return mode, get the rest of the data
    #         if self._ps2data[1] == 0x79:
    #             for x in range(0,12):
    #                 self._ps2data[x+9] = self.__shiftinout(0)
            
    #         GPIO.output(self.sel, GPIO.HIGH) # SEL_SET - disable joystick

    #         # Check to see if we received valid data or not.  
    #         # We should be in analog mode for our data to be valid (analog == 0x7_)
    #         if (self._ps2data[1] & 0xf0) == 0x70:
    #             break

    #         # If we got here, we are not in analog mode, try to recover...
    #         self.__reconfig() # try to get back into Analog mode.
    #         time.sleep(self.read_delay_s)
        
    #     # If we get here and still not in analog mode (=0x7_), try increasing the read_delay...
    #     if (self._ps2data[1] & 0xf0) != 0x70:
    #         if self.read_delay_s < 0.010: # 10ms
    #             self.read_delay_s += 0.001   # see if this helps out...

    #     # store the previous buttons states
    #     self.last_buttons = self.buttons 

    #     #store as one value for multiple functions
    #     self.buttons = (self._ps2data[4] << 8) + self._ps2data[3]

    #     self.last_millis = datetime.now().microsecond
    #     return ((self._ps2data[1] & 0xf0) == 0x70)  # True --> OK = analog mode - 0 --> NOT OK
