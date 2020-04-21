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
import time

MAX_PWM = 400
WAIT_TIME = 0.05
PWM_STEP = 10 # accel must be multiple of PWM_STEP = 10
DEPART_PWM = 200
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

        # self.pwm   = 0  # set initial pwm value for both motor -- forward or backward direction
        self.pwm_1 = 0  # set initial pwm value for motor 1 -- left or right direction
        self.pwm_2 = 0  # set initial pwm value for motor 2 -- left or right direction
        self.FORWARD = True # for outer use, not here
        self.BACKWARD = False # for outer use, not here

        cmd_0 = "{N0 M6}" # Set all motors to PWM mode
        cmd_1 = "{N0 P0}" # Set all motors to stand still
        cmd_0 = cmd_0.encode('utf-8')
        cmd_1 = cmd_1.encode('utf-8')
        self.__serial.write(cmd_0)
        time.sleep(WAIT_TIME/2) # stablize time
        self.__serial.write(cmd_1)

    def __del__(self):
        """
        Destructor
        """
        ## stop the motor if still running
        self.release()
        ## Close connection if still established
        if (self.__serial is not None and self.__serial.isOpen() == True):
            self.__serial.close()
    
    def __send(self, cmd): # format and send to the driver
        cmd = cmd.encode('utf-8')
        self.__serial.write(cmd) # send to the driver

    def __release(self, pwm_in): # support frame for release method
        time.sleep(WAIT_TIME) # give time for other task and slowly slow down

        pwm_out = 0 #  -STOP_PWM < pwm_in < STOP_PWM  --> stop now! so pwm_out = 0

        if pwm_in > STOP_PWM : # limiter for fw rotation, always > 0
            pwm_out = pwm_in - PWM_STEP # slow down a little bit
        elif pwm_in < -STOP_PWM : # limiter for bw rotation, always < 0
            pwm_out = pwm_in + PWM_STEP # slow down a little bit
        
        return pwm_out

    def release(self): # slow down slowly until really stop -  IMPORTANT function
        while self.pwm_1 != 0 or self.pwm_2 != 0 : # 0 is stable, so try your best to become one
            # --- if moving for/back
            if self.pwm_1 == self.pwm_2:
                self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
                self.pwm_2 = self.pwm_1 # make them equal again
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            # --- turning right
            elif abs(self.pwm_1) > abs(self.pwm_2):
                if self.pwm_2 != 0: # pwm_2 is supposed to be 0, if it's not zero, then reduce both until pwm_2 reaches zero
                    self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
                    self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    time.sleep(WAIT_TIME/2) # stablize time
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                else: # now pwm_2 is really 0, we can take care of pwm_1 fully
                    self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
            # --- turning left
            else: # abs(self.pwm_1) < abs(self.pwm_2)
                if self.pwm_1 != 0: # pwm_1 is supposed to be 0, if it's not zero, then reduce both until pwm_1 reaches zero
                    self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
                    self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    time.sleep(WAIT_TIME/2) # stablize time
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                else: # now pwm_1 is really 0, we can take care of pwm_2 fully
                    self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver

    # def release(self): # slow down slowly until really stop -  IMPORTANT function
    #     while self.pwm != 0 or self.pwm_1 != 0 or self.pwm_2 != 0 : # 0 is stable, so try your best to become one
    #         #################### Both Motor #####################
    #         if self.pwm != 0:
    #             self.pwm = self.__release(self.pwm) # calculate value to really slow down
    #             cmd = "{N0 P" + str(self.pwm) + "}" # {N1 P500} - set speed for pwm
    #             self.__send(cmd) # format and send to the driver
    #         else: # if not moving forward or backward, then check turn left and turn right
                
    #             #################### Motor 1 #####################
    #             if self.pwm_1 != 0:
    #                 self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
    #                 cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
    #                 self.__send(cmd) # format and send to the driver

    #             #################### Motor 2 #####################
    #             if self.pwm_2 != 0:
    #                 self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
    #                 cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
    #                 self.__send(cmd) # format and send to the driver


    def move_fw(self, accel): # move forward, so both motor rotate at the same time
        if self.pwm_1 == self.pwm_2: # system not turning
            if self.pwm_1 is 0 : # pwm_1 is equal pwm_2, so choose one to do math
                # self.pwm = DEPART_PWM # main object
                self.pwm_1 = DEPART_PWM
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            elif self.pwm_1 < MAX_PWM:
                # self.pwm += accel # faster a little bit
                self.pwm_1 += accel # faster a little bit
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            self.pwm_2 = self.pwm_1 # if pwm_1 changed, then change pwm_2
            # return nothing if systeam reached max speed
            return
        elif abs(self.pwm_1) > abs(self.pwm_2): # system is turning in some direction
            if self.pwm_1 > self.pwm_2: # positive value
                self.pwm_1 -= PWM_STEP # slower a little bit
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            # negative value will be released below
        else: # system is turning in the other direction: abs(self.pwm_1) < abs(self.pwm_2)
            if self.pwm_1 < self.pwm_2: # positive value
                self.pwm_2 -= PWM_STEP # slower a little bit
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
           # negative value will be released below
        self.release() # release for negative value since we are moving forward

    def move_bw(self, accel): # move backward, so both motor rotate at the same time
        if self.pwm_1 == self.pwm_2: # system not turning
            if self.pwm_1 is 0 : # pwm_1 is equal pwm_2, so choose one to do math
                # self.pwm = DEPART_PWM # main object
                self.pwm_1 = -DEPART_PWM
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            elif self.pwm_1 > -MAX_PWM:
                # self.pwm += accel # faster a little bit
                self.pwm_1 -= accel # faster a little bit
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            self.pwm_2 = self.pwm_1 # if pwm_1 changed, then change pwm_2
            # return nothing if systeam reached max speed
            return
        elif abs(self.pwm_1) > abs(self.pwm_2): # system is turning in some direction
            if self.pwm_1 < self.pwm_2: # negative value
                self.pwm_1 += PWM_STEP # slower a little bit
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            # positive value will be released below
        else: # system is turning in the other direction: abs(self.pwm_1) < abs(self.pwm_2)
            if self.pwm_1 > self.pwm_2: # negative value
                self.pwm_2 += PWM_STEP # slower a little bit
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
           # positive value will be released below
        self.release() # release for positive value since we are moving backward


    # def move_bw(self, accel): # move forward, so both motor rotate at the same time
    #     if self.pwm is 0 :
    #         self.pwm = -DEPART_PWM
    #         self.pwm_1 = DEPART_PWM
    #         self.pwm_2 = DEPART_PWM
    #     else:
    #         self.pwm -= accel # faster a little bit
    #         self.pwm_1 = self.pwm
    #         self.pwm_2 = self.pwm
    #     cmd = "{N0 P" + str(self.pwm) + "}" # {N1 P500} - set speed for pwm
    #     self.__send(cmd) # format and send to the driver

    def __turnright_fw(self, direction, accel):
        if direction: # if turn right in forward direction
            if self.pwm_1 < MAX_PWM:
                self.pwm_1 += accel # faster a little bit
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            elif self.pwm_1 > MAX_PWM:
                self.pwm_1 = MAX_PWM # protection if real speed is higher than limit
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            else: # self.pwm_1 == MAX_PWM
                if self.pwm_2 == 0 or abs(self.pwm_2) == DEPART_PWM: # reached max turning limit
                    return
                elif abs(self.pwm_2) < DEPART_PWM: # -DEPART_PWM < self.pwm_2 < DEPART_PWM, with no self.pwm_2 = 0
                    if self.pwm_2 > 0:
                        self.pwm_2 = DEPART_PWM  # set to be the limit
                    else:
                        self.pwm_2 = -DEPART_PWM  # set to be the limit
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # if pwm_2 can be reduced further
                    self.pwm_2 -= accel  # slower a little the other motor
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
        else: # if turn right in backward direction
            self.release()
            return
    
    def __turnright_bw(self, direction, accel):
        if direction: # if turn right in forward direction
            self.release()
            return
        else: # if turn right in backward direction
            if self.pwm_1 > -MAX_PWM:
                self.pwm_1 -= accel # faster a little bit
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            elif self.pwm_1 < -MAX_PWM:
                self.pwm_1 = -MAX_PWM # protection if real speed is higher than limit
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            else: # self.pwm_1 == -MAX_PWM
                if self.pwm_2 == 0 or abs(self.pwm_2) == DEPART_PWM: # reached max turning limit
                    return
                elif abs(self.pwm_2) < DEPART_PWM: # -DEPART_PWM < self.pwm_2 < DEPART_PWM, with no self.pwm_2 = 0
                    if self.pwm_2 > 0:
                        self.pwm_2 = DEPART_PWM  # set to be the limit
                    else:
                        self.pwm_2 = -DEPART_PWM  # set to be the limit
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # if pwm_2 can be reduced further
                    self.pwm_2 += accel  # slower a little the other motor
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return

    def turn_right(self, direction, accel): # turn right, so only one motor rotate at a time  |pwm_1| > |pwm_2|
        # --- if system is turning left instead, then slow down first
        if abs(self.pwm_1) < abs(self.pwm_2):
            if self.pwm_1 < self.pwm_2: # positive value
                self.pwm_2 -= PWM_STEP # slower a little bit
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            else: # negative value
                self.pwm_2 += PWM_STEP # slower a little bit
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
        # --- if system is standstill, moving for/back
        elif self.pwm_1 == self.pwm_2:
            # --- standstill
            if self.pwm_1 is 0 : 
                if direction: # if moving forward
                    self.pwm_1 = DEPART_PWM
                else: # if moving backward
                    self.pwm_1 = -DEPART_PWM
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            # --- moving forward
            elif self.pwm_1 > 0 :
                self.__turnright_fw(direction, accel)
                return
            # --- moving backward
            else : # self.pwm_1 < 0
                self.__turnright_bw(direction, accel)
                return
        else: # if system is really turning right: abs(self.pwm_1) > abs(self.pwm_2)
            if self.pwm_1 > self.pwm_2: # positive value
                self.__turnright_fw(direction, accel)
                return
            else: # negative value
                self.__turnright_bw(direction, accel)
                return

    def __turnleft_fw(self, direction, accel):
        if direction: # if turn right in forward direction
            if self.pwm_2 < MAX_PWM:
                self.pwm_2 += accel # faster a little bit
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            elif self.pwm_2 > MAX_PWM:
                self.pwm_2 = MAX_PWM # protection if real speed is higher than limit
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            else: # self.pwm_2 == MAX_PWM
                if self.pwm_1 == 0 or abs(self.pwm_1) == DEPART_PWM: # reached max turning limit
                    return
                elif abs(self.pwm_1) < DEPART_PWM: # -DEPART_PWM < self.pwm_1 < DEPART_PWM, with no self.pwm_1 = 0
                    if self.pwm_1 > 0:
                        self.pwm_1 = DEPART_PWM  # set to be the limit
                    else:
                        self.pwm_1 = -DEPART_PWM  # set to be the limit
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # if pwm_1 can be reduced further
                    self.pwm_1 -= accel  # slower a little the other motor
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
        else: # if turn right in backward direction
            self.release()
            return
    
    def __turnleft_bw(self, direction, accel):
        if direction: # if turn right in forward direction
            self.release()
            return
        else: # if turn right in backward direction
            if self.pwm_2 > -MAX_PWM:
                self.pwm_2 -= accel # faster a little bit
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            elif self.pwm_2 < -MAX_PWM:
                self.pwm_2 = -MAX_PWM # protection if real speed is higher than limit
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            else: # self.pwm_2 == -MAX_PWM
                if self.pwm_1 == 0 or abs(self.pwm_1) == DEPART_PWM: # reached max turning limit
                    return
                elif abs(self.pwm_1) < DEPART_PWM: # -DEPART_PWM < self.pwm_1 < DEPART_PWM, with no self.pwm_1 = 0
                    if self.pwm_1 > 0:
                        self.pwm_1 = DEPART_PWM  # set to be the limit
                    else:
                        self.pwm_1 = -DEPART_PWM  # set to be the limit
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # if pwm_1 can be reduced further
                    self.pwm_1 += accel  # slower a little the other motor
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return

    def turn_left(self, direction, accel): # turn left, so only one motor rotate at a time  |pwm_2| > |pwm_1|
        # --- if system is turning left instead, then slow down first
        if abs(self.pwm_2) < abs(self.pwm_1):
            if self.pwm_2 < self.pwm_1: # positive value
                self.pwm_1 -= PWM_STEP # slower a little bit
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            else: # negative value
                self.pwm_1 += PWM_STEP # slower a little bit
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
        # --- if system is standstill, moving for/back
        elif self.pwm_1 == self.pwm_2:
            # --- standstill
            if self.pwm_2 is 0 : 
                if direction: # if moving forward
                    self.pwm_2 = DEPART_PWM
                else: # if moving backward
                    self.pwm_2 = -DEPART_PWM
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            # --- moving forward
            elif self.pwm_2 > 0 :
                self.__turnleft_fw(direction, accel)
                return
            # --- moving backward
            else : # self.pwm_2 < 0
                self.__turnleft_bw(direction, accel)
                return
        else: # if system is really turning right: abs(self.pwm_2) > abs(self.pwm_1)
            if self.pwm_2 > self.pwm_1: # positive value
                self.__turnleft_fw(direction, accel)
                return
            else: # negative value
                self.__turnleft_bw(direction, accel)
                return

    # def turn_right(self, accel): # turn right, so only one motor rotate at a time  |pwm_1| > |pwm_2|
    #     if self.pwm_1 is 0 :
    #         self.pwm_1 = DEPART_PWM
    #     else:
    #         self.pwm_1 += accel # faster a little bit
    #     cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
    #     self.__send(cmd) # format and send to the driver

    # def turn_left(self, accel): # turn right, so only one motor rotate at a time
    #     if self.pwm_2 is 0 :
    #         self.pwm_2 = DEPART_PWM
    #     else:
    #         self.pwm_2 += accel # faster a little bit
    #     cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
    #     self.__send(cmd) # format and send to the driver
    