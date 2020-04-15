"""------------------------------------------------------------*-
  Init module for Motor driver module MSD_EM
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020
  version 1.00 - 15/04/2020
 --------------------------------------------------------------
 * Module created for the purpose of controlling the movement
 * of the UV robot.
 * Specifically designed for MSD_EM modules
 *
 * ref: http://www.cc-smart.net/vi/san-pham/msdem.html
 * detailed example on Arduino can be found at:
 * http://www.cc-smart.net/vi/san-pham/msdam.html
 *
 * {
//   MODE_TURNING = 0
//   MODE_SF_POSITION = 1
//   MODE_PID_POSITION = 2
//   MODE_PI_VELOCITY = 3
//   MODE_SMART_POSITION = 4
//   MODE_PI_VELOCITY_BY_ADC = 5
//   MODE_PWM = 6
//   
//   Example:  {N2  M6} --> change motor number 2 to PWM mode.

 * In this specific version, PWM mode will be used.
 --------------------------------------------------------------"""

import os
import serial
import struct

PWM_STEP = 10 # must be multiple of 10
DEPART_PWM = 300
STOP_PWM = 100 # value in which the motors almost don't move, so we can set them to zero immediately

class Motor_UART(object):
    """
    A python written library for the MSD_EM motor driver module.

    @attribute Serial __serial
    UART serial connection via PySerial.
    """

    def __init__(self, port='/dev/ttyUSB0', baudRate=115200):
        """
        Constructor
        @param port: a string dedicated to the connected device
        @param baudRate: an integer indicates the connection spped
        """
        if baudRate < 9600 or baudRate > 115200 or baudRate % 9600 != 0:
            raise ValueError('The given baudrate is invalid!')

        # Initialize PySerial connection
        self.__serial = serial.Serial(port=port,
                                      baudrate=baudRate,
                                      bytesize=serial.EIGHTBITS, 
                                      timeout=2
                                      )

        if self.__serial.isOpen():
            self.__serial.close()

        self.__serial.open()

        self.pwm   = 0  # set initial pwm value for both motor -- forward or backward direction
        self.pwm_1 = 0  # set initial pwm value for motor 1 -- left or right direction
        self.pwm_2 = 0  # set initial pwm value for motor 2 -- left or right direction


        cmd_0 = "{N0 M6}" # Set all motors to PWM mode
        cmd_1 = "{N0 P0}" # Set all motors to stand still
        cmd_0 = cmd_0.encode('utf-8')
        cmd_1 = cmd_1.encode('utf-8')
        self.__serial.write(cmd_0)
        self.__serial.write(cmd_1)

    def __del__(self):
        """
        Destructor
        """
        ## Close connection if still established
        if (self.__serial is not None and self.__serial.isOpen() == True):
            self.__serial.close()
    
    def __send(self, cmd): # format and send to the driver
        cmd = cmd.encode('utf-8')
        self.__serial.write(cmd) # send to the driver

    def __release(self, pwm): # support frame for release method
        if 0 < pwm < STOP_PWM : # limiter for fw rotation
            pwm = 0 # stop now
            return pwm
        elif pwm > STOP_PWM :
            pwm -= PWM_STEP # slow down a little bit
            return pwm

        if 0 > pwm > -STOP_PWM : # limiter for bw rotation
            pwm = 0 # stop now
            return pwm
        else:
            pwm += PWM_STEP # slow down a little bit
            return pwm

    def release(self): # slow down slowly until really stop -  IMPORTANT function
        while self.pwm != 0 or self.pwm_1 != 0 or self.pwm_2 != 0 : # 0 is stable, so try your best to become one
            #################### Both Motor #####################
            if self.pwm != 0:
                self.pwm = self.__release(self.pwm) # calculate value to really slow down
                cmd = "{N0 P" + str(self.pwm) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            else: # if not moving forward or backward, then check turn left and turn right
                
                #################### Motor 1 #####################
                if self.pwm_1 != 0:
                    self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver

                #################### Motor 2 #####################
                if self.pwm_2 != 0:
                    self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver


    def move_fw(self, accel): # move forward, so both motor rotate at the same time
        if self.pwm is 0 :
            self.pwm = DEPART_PWM
        else
            self.pwm += accel # faster a little bit
        cmd = "{N0 P" + str(self.pwm) + "}" # {N1 P500} - set speed for pwm
        self.__send(cmd) # format and send to the driver

    def move_bw(self, accel): # move forward, so both motor rotate at the same time
        if self.pwm is 0 :
            self.pwm = DEPART_PWM
        else
            self.pwm -= accel # slower a little bit
        cmd = "{N0 P" + str(self.pwm) + "}" # {N1 P500} - set speed for pwm
        self.__send(cmd) # format and send to the driver

    def turn_right(self, accel): # turn right, so only one motor rotate at a time
        if self.pwm_1 is 0 :
            self.pwm_1 = DEPART_PWM
        else
            self.pwm_1 += accel # faster a little bit
        cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
        self.__send(cmd) # format and send to the driver

    def turn_left(self, accel): # turn right, so only one motor rotate at a time
        if self.pwm_2 is 0 :
            self.pwm_2 = DEPART_PWM
        else
            self.pwm_2 += accel # faster a little bit
        cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
        self.__send(cmd) # format and send to the driver
    