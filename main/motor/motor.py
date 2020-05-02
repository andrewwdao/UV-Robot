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

################# constant for PID #######################
RAD_STEP = 1 # radian
# SEND_INTERVAL depends on the ps2, maximum 250kHz

################# constant for PWM #######################
WAIT_TIME = 5 #ms
PWM_STEP = 30 # accel must be multiple of PWM_STEP = 10
MINIMUM_DIF = 50
DEPART_PWM = 120
STOP_PWM = 100 # value in which the motors almost don't move, so we can set them to zero immediately
# MAX_PWM declared inside the class

millis = lambda: int(time.time() * 1000)

class MotorUART_PID(object):
    """
    A python written library for the MSD_EM motor driver module.

    @attribute Serial __serial
    UART serial connection via PySerial.
    """

    def __init__(self, port='/dev/ttyUSB0', baudRate=250000, speed = 200):
        """
        Constructor
        @param port: a string dedicated to the connected device
        @param baudRate: an integer indicates the connection spped
        """
        if baudRate < 9600 or baudRate > 250000:
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

        self.MAX_SPEED = speed # initial maxspeed of the system
        self.pos_1 = 0   # set initial position value for motor 1
        self.speed_1 = 0 # set initial speed value for motor 1
        self.pos_2 = 0   # set initial position value for motor 2
        self.speed_2 = 0 # set initial speed value for motor 2
        self.FORWARD = True # const, for outer use in main, not here
        self.BACKWARD = False # const, for outer use in main, not here
        self.MV_FW = True # flag indicates when moving forward, default to be Forward
        

        #   MODE_TURNING = 0
        #   MODE_SF_POSITION = 1
        #   MODE_PID_POSITION = 2
        #   MODE_PI_VELOCITY = 3
        #   MODE_SMART_POSITION = 4
        #   MODE_PI_VELOCITY_BY_ADC = 5
        #   MODE_PWM = 6
        starter_cmd = "{N0 M2 A2000 R}" # Set all motors to PID mode, with Acceleration = 2000, reset position --> will also make all motors stop
        starter_cmd = starter_cmd.encode('utf-8')
        self.__serial.write(starter_cmd)
        print("Motor ready!")

    def __del__(self):
        """
        Destructor
        """
        ## stop the motor if still running
        self.clean()

    def clean(self):
        ## stop the motor if still running
        self.release(False, 1)
        ## Close connection if still established
        if (self.__serial is not None and self.__serial.isOpen() == True):
            self.__serial.close()
    
    def __send(self, cmd): # format and send to the driver
        cmd = cmd.encode('utf-8')
        self.__serial.write(cmd) # send to the driver

    def __send2by1(self):
        cmd = "{N0 P" + str(self.pos_1) + " V" + str(self.speed_1) + "}" # {N1 P500 V100} - set position and speed for PID
        self.__send(cmd) # format and send to the driver
                
    def __send2by2(self):
        cmd_1 = "{N1 P" + str(self.pos_1) + " V" + str(self.speed_1) + "}" # {N1 P500 V100} - set position and speed for PID
        cmd_2 = "{N2 P" + str(self.pos_2) + " V" + str(self.speed_2) + "}" # {N2 P500 V100} - set position and speed for PID
        self.__send(cmd_1) # format and send to the driver
        time.sleep(0.001)  # sleep for 1ms
        self.__send(cmd_2) # format and send to the driver

    def release(self, hold_flag, accel): # slow down slowly until really stop -  IMPORTANT function
        if hold_flag: # time flag to make the system run as is for a short time
            if self.MV_FW == True: # correct direction to make them run
                self.pos_1 += accel # move a little bit in forward direction
                self.pos_2 += accel # move a little bit in forward direction
            else:
                self.pos_1 -= accel # move a little bit in forward direction
                self.pos_2 -= accel # move a little bit in forward direction
            self.__send2by2()
        elif self.speed_1 != 0 or self.speed_2 != 0 : # 0 is stable, so try your best to become one
            if self.MV_FW == True: # bias direction to make them stop
                self.pos_1 -= accel # move a little bit in forward direction
                self.pos_2 -= accel # move a little bit in forward direction
            else:
                self.pos_1 += accel # move a little bit in forward direction
                self.pos_2 += accel # move a little bit in forward direction
            # --- if moving for/back
            if self.speed_1 == self.speed_2:
                self.speed_1 -= accel # calculate value to really slow down
                self.speed_2 = self.speed_1 # make them equal again
                self.__send2by1()
                return
            # --- turning right
            elif self.speed_1 > self.speed_2:
                if self.speed_2 != 0: # speed_2 is supposed to be 0, if it's not zero, then reduce both until speed_2 reaches zero
                    self.speed_1 -= accel # calculate value to really slow down
                    self.speed_2 -= accel # calculate value to really slow down
                else: # now speed_2 is really 0, we can take care of speed_1 fully
                    self.speed_1 -= accel # calculate value to really slow down  
            # --- turning left
            else: # self.speed_1 < self.speed_2
                if self.pos_1 != 0: # pos_1 is supposed to be 0, if it's not zero, then reduce both until pos_1 reaches zero
                    self.speed_1 -= accel # calculate value to really slow down
                    self.speed_2 -= accel # calculate value to really slow down
                else: # now speed_1 is really 0, we can take care of speed_2 fully
                    self.speed_2 -= accel # calculate value to really slow down  
            self.__send2by2()

    def __move(self, accel, moving_forward):
        # --- if something wrong happened and speed return negative
        if self.speed_1 < 0 or self.speed_2 < 0:
            self.speed_2 = self.speed_1 = 0
            print('speed return negative! reseting...')
            return
        # --- if it is moving in bias direction with the moving_forward flag, including in releasing mode
        elif (self.MV_FW == ~moving_forward) & (self.speed_1|self.speed_2 != 0):
            if self.speed_1 == self.speed_2: # system not turning, speed_1 is equal speed_2, so choose one to do math
                self.speed_1 -= accel # slower a little bit
                self.speed_2 = self.speed_1
                self.__send2by1() # send common command for both motors
                return
            elif self.speed_1 > self.speed_2: # system is turning in some direction, speed always > 0 so no worry
                if self.speed_2 is 0:
                    self.speed_1 -= accel # slower a little bit
                else: # self.speed_2 != 0
                    self.speed_1 -= accel # slower a little bit
                    self.speed_2 -= accel # slower a little bit
            else: # self.speed_1 < self.speed_2
                if self.speed_1 is 0:
                    self.speed_2 -= accel # slower a little bit
                else: # self.speed_1 != 0
                    self.speed_1 -= accel # slower a little bit
                    self.speed_2 -= accel # slower a little bit
            
        # --- if it is in the correct direction realm
        else:
            self.MV_FW = moving_forward # set flag for global
        if self.speed_1 == self.speed_2: # system not turning, speed_1 is equal speed_2, so choose one to do math
            if self.speed_1 < self.MAX_SPEED:
                self.speed_1 += accel # faster a little bit
                self.speed_2 = self.speed_1
            self.__send2by1() # send common command for both motors
        elif self.speed_1 > self.speed_2: # system is turning in some direction, speed always > 0 so no worry
            self.speed_2 += accel # faster a little bit
        else: # self.speed_1 < self.speed_2
            self.speed_1 += accel # faster a little bit
        
        # finally send command to motors
        self.__send2by2() # send command for 2 motors separately

    def move_fw(self, accel): # move forward, so both motor rotate at the same time
        self.pos_1 += accel # move a little bit in forward direction
        self.pos_2 = self.pos_1
        self.__move(accel, moving_forward=True)

    def move_bw(self, accel): # move backward, so both motor rotate at the same time
        self.pos_1 -= accel # move a little bit in backward direction
        self.pos_2 = self.pos_1
        self.__move(accel, moving_forward=False)
 
    def turn_right(self, direction, accel): # turn right, so only one motor rotate at a time  |pos_1| > |pos_2|
        # --- if something wrong happened and speed return negative
        if self.speed_1 < 0 or self.speed_2 < 0:
            self.speed_2 = self.speed_1 = 0
            print('speed return negative! reseting...')
            return
        # --- if it is moving forward in any direction, including in releasing mode
        elif self.MV_FW == True:
            self.pos_1 += accel # move a little bit in forward direction
            if self.speed_2 > 0:
                self.pos_2 += accel # move a little bit in forward direction
        # --- if it is moving backward in any direction, including in releasing mode
        else:
            self.pos_1 -= accel # move a little bit in forward direction
            if self.speed_2 > 0:
                self.pos_2 -= accel # move a little bit in forward direction

        if self.speed_1 < self.speed_2: # system is turning in opposite 
            self.speed_2 -= accel # slower a little bit
        else:# self.speed_1 >= self.speed_2: # system is moving forward or in correct turning
            self.speed_1 += accel # faster a little bit

        self.__send2by2()

    def turn_left(self, direction, accel): # turn left, so only one motor rotate at a time  |pos_2| > |pos_1|
        # --- if something wrong happened and speed return negative
        if self.speed_1 < 0 or self.speed_2 < 0:
            self.speed_2 = self.speed_1 = 0
            print('speed return negative! reseting...')
            return
        # --- if it is moving forward in any direction, including in releasing mode
        elif self.MV_FW == True:
            self.pos_1 += accel # move a little bit in forward direction
            if self.speed_2 > 0:
                self.pos_2 += accel # move a little bit in forward direction
        # --- if it is moving backward in any direction, including in releasing mode
        else:
            self.pos_1 -= accel # move a little bit in forward direction
            if self.speed_2 > 0:
                self.pos_2 -= accel # move a little bit in forward direction

        if self.speed_2 < self.speed_1: # system is turning in opposite 
            self.speed_1 -= accel # slower a little bit
        else:# self.speed_2 >= self.speed_1: # system is moving forward or in correct turning
            self.speed_2 += accel # faster a little bit

        self.__send2by2()

class MotorUART_PWM(object):
    """
    A python written library for the MSD_EM motor driver module.

    @attribute Serial __serial
    UART serial connection via PySerial.
    """

    def __init__(self, port='/dev/ttyUSB0', baudRate=115200, speed = 400):
        """
        Constructor
        @param port: a string dedicated to the connected device
        @param baudRate: an integer indicates the connection spped
        """
        if baudRate < 9600 or baudRate > 1000000:
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

        self.pwm_1 = 0  # set initial pwm value for motor 1 -- left or right direction
        self.pwm_2 = 0  # set initial pwm value for motor 2 -- left or right direction
        self.FORWARD = True # for outer use, not here
        self.BACKWARD = False # for outer use, not here
        self.MAX_PWM = speed
        self.last_millis = millis()
        """
          MODE_TURNING = 0
          MODE_SF_POSITION = 1
          MODE_PID_POSITION = 2
          MODE_PI_VELOCITY = 3
          MODE_SMART_POSITION = 4
          MODE_PI_VELOCITY_BY_ADC = 5
          MODE_PWM = 6
        """
        cmd_0 = "{N0 M6}" # Set all motors to PWM mode
        cmd_1 = "{N0 P0}" # Set all motors to stand still
        cmd_0 = cmd_0.encode('utf-8')
        cmd_1 = cmd_1.encode('utf-8')
        self.__serial.write(cmd_0)
        time.sleep(0.001) # stablize time
        self.__serial.write(cmd_1)
        print("Motor ready!")

    def __del__(self):
        """
        Destructor
        """
        ## stop the motor if still running
        self.clean()

    def clean(self):
        ## stop the motor if still running
        self.release()
        ## Close connection if still established
        if (self.__serial is not None and self.__serial.isOpen() == True):
            self.__serial.close()
            
    def __send(self, cmd): # format and send to the driver
        cmd = cmd.encode('utf-8')
        self.__serial.write(cmd) # send to the driver

    def __release(self, pwm_in): # support frame for release method
        pwm_out = 0 #  -STOP_PWM < pwm_in < STOP_PWM  --> stop now! so pwm_out = 0

        if pwm_in > STOP_PWM : # limiter for fw rotation, always > 0
            pwm_out = pwm_in - PWM_STEP # slow down a little bit
        elif pwm_in < -STOP_PWM : # limiter for bw rotation, always < 0
            pwm_out = pwm_in + PWM_STEP # slow down a little bit
        
        return pwm_out

    def release(self): # slow down slowly until really stop -  IMPORTANT function
        if self.pwm_1 == self.pwm_2 == 0:
            return False # done works, so return false
        elif (millis()- self.last_millis) > WAIT_TIME: # self.pwm_1 != 0 or self.pwm_2 != 0, 0 is stable, so try your best to become one
            self.last_millis = millis() # reset counter
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
                    time.sleep(0.001) # stablize time
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
                    time.sleep(0.001) # stablize time
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                else: # now pwm_1 is really 0, we can take care of pwm_2 fully
                    self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
        return True # not done work yet, so return True
    

    """
    only 6 direction: Straight, Left, Right * (Forward, Backward)
    """
    def move_fw(self, accel): # move forward, so both motor rotate at the same time
        if self.pwm_1 == self.pwm_2: # system not turning, straight forward or backward
            if abs(self.pwm_1) < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
                self.pwm_1 = DEPART_PWM
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            elif self.pwm_1 < self.MAX_PWM:
                self.pwm_1 += accel # faster a little bit
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            self.pwm_2 = self.pwm_1 # if pwm_1 changed, then change pwm_2
            return
        elif abs(self.pwm_1) > abs(self.pwm_2): # system is turning in some direction
            if self.pwm_1 > self.pwm_2: # positive value
                if -DEPART_PWM < self.pwm_2 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
                    self.pwm_2 = DEPART_PWM
                elif abs(self.pwm_1-self.pwm_2) < MINIMUM_DIF:
                    self.pwm_2 = self.pwm_1
                else:
                    self.pwm_2 += PWM_STEP # faster a little bit to make it fast enough with the other
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            # negative value will be released below
        else: # abs(self.pwm_1) < abs(self.pwm_2): system is turning in the other direction
            if self.pwm_1 < self.pwm_2: # positive value
                if -DEPART_PWM < self.pwm_1 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
                    self.pwm_1 = DEPART_PWM
                elif abs(self.pwm_2-self.pwm_1) < MINIMUM_DIF:
                    self.pwm_1 = self.pwm_2
                else:
                    self.pwm_1 += PWM_STEP # faster a little bit to make it fast enough with the other
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
           # negative value will be released below
        self.release() # release for negative value since we are moving forward

    def move_bw(self, accel): # move backward, so both motor rotate at the same time
        if self.pwm_1 == self.pwm_2: # system not turning
            if -DEPART_PWM < self.pwm_1 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
                self.pwm_1 = -DEPART_PWM
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            elif self.pwm_1 > -self.MAX_PWM:
                self.pwm_1 -= accel # faster a little bit
                cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
            self.pwm_2 = self.pwm_1 # if pwm_1 changed, then change pwm_2
            return
        elif abs(self.pwm_1) > abs(self.pwm_2): # system is turning in some direction
            if self.pwm_1 < self.pwm_2: # negative value
                if -DEPART_PWM < self.pwm_2 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
                    self.pwm_2 = -DEPART_PWM
                elif abs(self.pwm_1-self.pwm_2) < MINIMUM_DIF:
                    self.pwm_2 = self.pwm_1
                else:
                    self.pwm_2 -= PWM_STEP # faster a little bit to make it fast enough with the other
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            # positive value will be released below
        else: # system is turning in the other direction: abs(self.pwm_1) < abs(self.pwm_2)
            if self.pwm_1 > self.pwm_2: # negative value
                if -DEPART_PWM < self.pwm_1 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
                    self.pwm_1 = -DEPART_PWM
                elif abs(self.pwm_2-self.pwm_1) < MINIMUM_DIF:
                    self.pwm_1 = self.pwm_2
                else:
                    self.pwm_1 -= PWM_STEP # faster a little bit to make it fast enough with the other
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
           # positive value will be released below
        self.release() # release for positive value since we are moving backward

    def turn_right(self, direction, accel): # turn right, so only one motor rotate at a time  |pwm_1| > |pwm_2|
        # --- if system is standstill, moving for/back
        if self.pwm_1 == self.pwm_2:
            # --- standstill
            if abs(self.pwm_1) < STOP_PWM : 
                if direction: # if moving forward
                    self.pwm_1 = DEPART_PWM
                else: # if moving backward
                    self.pwm_1 = -DEPART_PWM
                cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            # --- moving forward
            elif self.pwm_1 > STOP_PWM : # absolutely > 0
                if self.pwm_1 < self.MAX_PWM:
                    self.pwm_1 += accel # faster a little bit
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                elif self.pwm_1 > self.MAX_PWM:
                    self.pwm_1 = self.pwm_2 = self.MAX_PWM # protection if real speed is higher than limit
                    cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # self.pwm_1 == self.MAX_PWM, so self.pwm_2 == self.MAX_PWM too
                    self.pwm_2 -= DEPART_PWM  # slower the other motor
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
            # --- moving backward
            else : # self.pwm_1 < -STOP_PWM
                if self.pwm_1 > -self.MAX_PWM:
                    self.pwm_1 -= accel # faster a little bit
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                elif self.pwm_1 < -self.MAX_PWM:
                    self.pwm_1 = self.pwm_2 = -self.MAX_PWM # protection if real speed is higher than limit
                    cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # self.pwm_1 == -self.MAX_PWM, so self.pwm_2 == -self.MAX_PWM too
                    self.pwm_2 += DEPART_PWM  # slower a little the other motor
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
        # --- if system is turning left instead, then make the right wheel faster
        elif abs(self.pwm_1) < abs(self.pwm_2):
            if abs(self.pwm_2-self.pwm_1) < MINIMUM_DIF:
                self.pwm_1 = self.pwm_2
            elif self.pwm_1 < self.pwm_2: # postitive value
                self.pwm_1 += PWM_STEP # faster a little bit to make it fast enough with the other
            else: # self.pwm_1 > self.pwm_2, negative value
                self.pwm_1 -= PWM_STEP # faster a little bit to make it fast enough with the other
            cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
            self.__send(cmd) # format and send to the driver
            return
        else: # if system is really turning right: abs(self.pwm_1) > abs(self.pwm_2)
            if self.pwm_1 > self.pwm_2: # positive value
                if self.pwm_1 < self.MAX_PWM:
                    self.pwm_1 += accel # faster a little bit
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                elif self.pwm_1 > self.MAX_PWM:
                    self.pwm_1 = self.MAX_PWM # protection if real speed is higher than limit
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # self.pwm_1 == self.MAX_PWM, so self.pwm_2 == self.MAX_PWM too
                    if self.pwm_2 == 0 or abs(self.pwm_2) == DEPART_PWM: # reached max turning limit
                        return
                    if abs(self.pwm_2) < DEPART_PWM:
                        self.pwm_2 = DEPART_PWM
                    else:
                        self.pwm_2 -= accel  # slower a little the other motor
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
            else: # self.pwm_1 < self.pwm_2, negative value
                if self.pwm_1 > -self.MAX_PWM:
                    self.pwm_1 -= accel # faster a little bit
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                elif self.pwm_1 < -self.MAX_PWM:
                    self.pwm_1 = -self.MAX_PWM # protection if real speed is higher than limit
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # self.pwm_1 == self.MAX_PWM, so self.pwm_2 == self.MAX_PWM too
                    if self.pwm_2 == 0 or abs(self.pwm_2) == DEPART_PWM: # reached max turning limit
                        return
                    if abs(self.pwm_2) < DEPART_PWM:
                        self.pwm_2 = -DEPART_PWM
                    else:
                        self.pwm_2 += accel  # slower a little the other motor
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return


    def turn_left(self, direction, accel): # turn right, so only one motor rotate at a time  |pwm_1| > |pwm_2|
        # --- if system is standstill, moving for/back
        if self.pwm_1 == self.pwm_2:
            # --- standstill
            if abs(self.pwm_2) < STOP_PWM : 
                if direction: # if moving forward
                    self.pwm_2 = DEPART_PWM
                else: # if moving backward
                    self.pwm_2 = -DEPART_PWM
                cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                self.__send(cmd) # format and send to the driver
                return
            # --- moving forward
            elif self.pwm_2 > STOP_PWM : # absolutely > 0
                if self.pwm_2 < self.MAX_PWM:
                    self.pwm_2 += accel # faster a little bit
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                elif self.pwm_2 > self.MAX_PWM:
                    self.pwm_1 = self.pwm_2 = self.MAX_PWM # protection if real speed is higher than limit
                    cmd = "{N0 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # self.pwm_2 == self.MAX_PWM, so self.pwm_1 == self.MAX_PWM too
                    self.pwm_1 -= accel  # slower a little the other motor
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
            # --- moving backward
            else : # self.pwm_2 < -STOP_PWM
                if self.pwm_2 > -self.MAX_PWM:
                    self.pwm_2 -= accel # faster a little bit
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                elif self.pwm_2 < -self.MAX_PWM:
                    self.pwm_1 = self.pwm_2 = -self.MAX_PWM # protection if real speed is higher than limit
                    cmd = "{N0 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # self.pwm_2 == -self.MAX_PWM, so self.pwm_1 == -self.MAX_PWM too
                    self.pwm_1 += accel  # slower a little the other motor
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
        # --- if system is turning right instead, then make the left wheel faster
        elif abs(self.pwm_1) > abs(self.pwm_2):
            if abs(self.pwm_1-self.pwm_2) < MINIMUM_DIF:
                self.pwm_2 = self.pwm_1
            elif self.pwm_2 < self.pwm_1: # postitive value
                self.pwm_2 += PWM_STEP # faster a little bit to make it fast enough with the other
            else: # self.pwm_2 > self.pwm_1, negative value
                self.pwm_2 -= PWM_STEP # faster a little bit to make it fast enough with the other
            cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
            self.__send(cmd) # format and send to the driver
            return
        else: # if system is really turning left: abs(self.pwm_1) < abs(self.pwm_2)
            if self.pwm_2 > self.pwm_1: # positive value
                if self.pwm_2 < self.MAX_PWM:
                    self.pwm_2 += accel # faster a little bit
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                elif self.pwm_2 > self.MAX_PWM:
                    self.pwm_2 = self.MAX_PWM # protection if real speed is higher than limit
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # self.pwm_2 == self.MAX_PWM, so self.pwm_1 == self.MAX_PWM too
                    if self.pwm_1 == 0 or abs(self.pwm_1) == DEPART_PWM: # reached max turning limit
                        return
                    if abs(self.pwm_1) < DEPART_PWM:
                        self.pwm_1 = DEPART_PWM
                    else:
                        self.pwm_1 -= accel  # slower a little the other motor
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
            else: # self.pwm_2 < self.pwm_1, negative value
                if self.pwm_2 > -self.MAX_PWM:
                    self.pwm_2 -= accel # faster a little bit
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                elif self.pwm_2 < -self.MAX_PWM:
                    self.pwm_2 = -self.MAX_PWM # protection if real speed is higher than limit
                    cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return
                else: # self.pwm_2 == self.MAX_PWM, so self.pwm_1 == self.MAX_PWM too
                    if self.pwm_1 == 0 or abs(self.pwm_1) == DEPART_PWM: # reached max turning limit
                        return
                    if abs(self.pwm_1) < DEPART_PWM:
                        self.pwm_1 = -DEPART_PWM
                    else:
                        self.pwm_1 += accel  # slower a little the other motor
                    cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
                    self.__send(cmd) # format and send to the driver
                    return

# class MotorUART_PWM(object):
#     """
#     A python written library for the MSD_EM motor driver module.

#     @attribute Serial __serial
#     UART serial connection via PySerial.
#     """

#     def __init__(self, port='/dev/ttyUSB0', baudRate=115200, speed = 400):
#         """
#         Constructor
#         @param port: a string dedicated to the connected device
#         @param baudRate: an integer indicates the connection spped
#         """
#         if baudRate < 9600 or baudRate > 1000000:
#             raise ValueError('The given baudrate is invalid!')

#         # Initialize PySerial connection
#         self.__serial = serial.Serial(port=port,
#                                       baudrate=baudRate,
#                                       bytesize=serial.EIGHTBITS, 
#                                       timeout=2
#                                       )

#         if self.__serial.isOpen():
#             self.__serial.close()

#         self.__serial.open()

#         self.pwm_1 = 0  # set initial pwm value for motor 1 -- left or right direction
#         self.pwm_2 = 0  # set initial pwm value for motor 2 -- left or right direction
#         self.FORWARD = True # for outer use, not here
#         self.BACKWARD = False # for outer use, not here
#         self.MAX_PWM = speed
#         self.last_millis = millis()
#         """
#           MODE_TURNING = 0
#           MODE_SF_POSITION = 1
#           MODE_PID_POSITION = 2
#           MODE_PI_VELOCITY = 3
#           MODE_SMART_POSITION = 4
#           MODE_PI_VELOCITY_BY_ADC = 5
#           MODE_PWM = 6
#         """
#         cmd_0 = "{N0 M6}" # Set all motors to PWM mode
#         cmd_1 = "{N0 P0}" # Set all motors to stand still
#         cmd_0 = cmd_0.encode('utf-8')
#         cmd_1 = cmd_1.encode('utf-8')
#         self.__serial.write(cmd_0)
#         time.sleep(0.001) # stablize time
#         self.__serial.write(cmd_1)
#         print("Motor ready!")

#     def __del__(self):
#         """
#         Destructor
#         """
#         ## stop the motor if still running
#         self.clean()

#     def clean(self):
#         ## stop the motor if still running
#         self.release()
#         ## Close connection if still established
#         if (self.__serial is not None and self.__serial.isOpen() == True):
#             self.__serial.close()
            
#     def __send(self, cmd): # format and send to the driver
#         cmd = cmd.encode('utf-8')
#         self.__serial.write(cmd) # send to the driver

#     def __release(self, pwm_in): # support frame for release method
#         pwm_out = 0 #  -STOP_PWM < pwm_in < STOP_PWM  --> stop now! so pwm_out = 0

#         if pwm_in > STOP_PWM : # limiter for fw rotation, always > 0
#             pwm_out = pwm_in - PWM_STEP # slow down a little bit
#         elif pwm_in < -STOP_PWM : # limiter for bw rotation, always < 0
#             pwm_out = pwm_in + PWM_STEP # slow down a little bit
        
#         return pwm_out

#     def release(self): # slow down slowly until really stop -  IMPORTANT function
#         if self.pwm_1 == self.pwm_2 == 0:
#             return False # done works, so return false
#         elif (millis()- self.last_millis) > WAIT_TIME: # self.pwm_1 != 0 or self.pwm_2 != 0, 0 is stable, so try your best to become one
#             self.last_millis = millis() # reset counter
#             # --- if moving for/back
#             if self.pwm_1 == self.pwm_2:
#                 self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
#                 self.pwm_2 = self.pwm_1 # make them equal again
#                 cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#             # --- turning right
#             elif abs(self.pwm_1) > abs(self.pwm_2):
#                 if self.pwm_2 != 0: # pwm_2 is supposed to be 0, if it's not zero, then reduce both until pwm_2 reaches zero
#                     self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
#                     self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
#                     cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     time.sleep(0.001) # stablize time
#                     cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                 else: # now pwm_2 is really 0, we can take care of pwm_1 fully
#                     self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
#                     cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#             # --- turning left
#             else: # abs(self.pwm_1) < abs(self.pwm_2)
#                 if self.pwm_1 != 0: # pwm_1 is supposed to be 0, if it's not zero, then reduce both until pwm_1 reaches zero
#                     self.pwm_1 = self.__release(self.pwm_1) # calculate value to really slow down
#                     self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
#                     cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     time.sleep(0.001) # stablize time
#                     cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                 else: # now pwm_1 is really 0, we can take care of pwm_2 fully
#                     self.pwm_2 = self.__release(self.pwm_2) # calculate value to really slow down
#                     cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#         return True # not done work yet, so return True
    
#     def move_fw(self, accel): # move forward, so both motor rotate at the same time
#         if self.pwm_1 == self.pwm_2: # system not turning
#             if -DEPART_PWM < self.pwm_1 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
#                 self.pwm_1 = DEPART_PWM
#                 cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#             elif self.pwm_1 < self.MAX_PWM:
#                 self.pwm_1 += accel # faster a little bit
#                 cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#             self.pwm_2 = self.pwm_1 # if pwm_1 changed, then change pwm_2
#             return
#         elif abs(self.pwm_1) > abs(self.pwm_2): # system is turning in some direction
#             if self.pwm_1 > self.pwm_2: # positive value
#                 if -DEPART_PWM < self.pwm_2 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
#                     self.pwm_2 = DEPART_PWM
#                 else:
#                     self.pwm_2 += PWM_STEP # faster a little bit to make it fast enough with the other
#                 cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             # negative value will be released below
#         else: # system is turning in the other direction: abs(self.pwm_1) < abs(self.pwm_2)
#             if self.pwm_1 < self.pwm_2: # positive value
#                 if -DEPART_PWM < self.pwm_1 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
#                     self.pwm_1 = DEPART_PWM
#                 else:
#                     self.pwm_1 += PWM_STEP # faster a little bit to make it fast enough with the other
#                 cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#            # negative value will be released below
#         self.release() # release for negative value since we are moving forward

#     def move_bw(self, accel): # move backward, so both motor rotate at the same time
#         if self.pwm_1 == self.pwm_2: # system not turning
#             if -DEPART_PWM < self.pwm_1 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
#                 self.pwm_1 = -DEPART_PWM
#                 cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#             elif self.pwm_1 > -self.MAX_PWM:
#                 self.pwm_1 -= accel # faster a little bit
#                 cmd = "{N0 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#             self.pwm_2 = self.pwm_1 # if pwm_1 changed, then change pwm_2
#             return
#         elif abs(self.pwm_1) > abs(self.pwm_2): # system is turning in some direction
#             if self.pwm_1 < self.pwm_2: # negative value
#                 if -DEPART_PWM < self.pwm_2 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
#                     self.pwm_2 = -DEPART_PWM
#                 else:
#                     self.pwm_2 -= PWM_STEP # faster a little bit to make it fast enough with the other
#                 cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             # positive value will be released below
#         else: # system is turning in the other direction: abs(self.pwm_1) < abs(self.pwm_2)
#             if self.pwm_1 > self.pwm_2: # negative value
#                 if -DEPART_PWM < self.pwm_1 < DEPART_PWM: # pwm_1 is equal pwm_2, so choose one to do math
#                     self.pwm_1 = -DEPART_PWM
#                 else:
#                     self.pwm_1 -= PWM_STEP # faster a little bit to make it fast enough with the other
#                 cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#            # positive value will be released below
#         self.release() # release for positive value since we are moving backward
    
#     def __turnright_fw(self, direction, accel):
#         if direction: # if turn right in forward direction
#             if self.pwm_1 < self.MAX_PWM:
#                 if -DEPART_PWM < self.pwm_1 < DEPART_PWM:
#                     self.pwm_1 = DEPART_PWM
#                 else:
#                     self.pwm_1 += accel # faster a little bit
#                 cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             elif self.pwm_1 > self.MAX_PWM:
#                 self.pwm_1 = self.MAX_PWM # protection if real speed is higher than limit
#                 cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             else: # self.pwm_1 == self.MAX_PWM
#                 if self.pwm_2 == 0 or abs(self.pwm_2) == DEPART_PWM: # reached max turning limit
#                     return
#                 elif abs(self.pwm_2) < DEPART_PWM: # -DEPART_PWM < self.pwm_2 < DEPART_PWM, with no self.pwm_2 = 0
#                     if self.pwm_2 > 0:
#                         self.pwm_2 = DEPART_PWM  # set to be the limit
#                     else:
#                         self.pwm_2 = -DEPART_PWM  # set to be the limit
#                     cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     return
#                 else: # if pwm_2 can be reduced further
#                     self.pwm_2 -= accel  # slower a little the other motor
#                     cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     return
#         else: # if turn right in backward direction
#             self.release()
#             return
    
#     def __turnright_bw(self, direction, accel):
#         if direction: # if turn right in forward direction
#             self.release()
#             return
#         else: # if turn right in backward direction
#             if self.pwm_1 > -self.MAX_PWM:
#                 if -DEPART_PWM < self.pwm_1 < DEPART_PWM:
#                     self.pwm_1 = -DEPART_PWM
#                 else:
#                     self.pwm_1 -= accel # faster a little bit
#                 cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             elif self.pwm_1 < -self.MAX_PWM:
#                 self.pwm_1 = -self.MAX_PWM # protection if real speed is higher than limit
#                 cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             else: # self.pwm_1 == -self.MAX_PWM
#                 if self.pwm_2 == 0 or abs(self.pwm_2) == DEPART_PWM: # reached max turning limit
#                     return
#                 elif abs(self.pwm_2) < DEPART_PWM: # -DEPART_PWM < self.pwm_2 < DEPART_PWM, with no self.pwm_2 = 0
#                     if self.pwm_2 > 0:
#                         self.pwm_2 = DEPART_PWM  # set to be the limit
#                     else:
#                         self.pwm_2 = -DEPART_PWM  # set to be the limit
#                     cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     return
#                 else: # if pwm_2 can be reduced further
#                     self.pwm_2 += accel  # slower a little the other motor
#                     cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     return

#     def turn_right(self, direction, accel): # turn right, so only one motor rotate at a time  |pwm_1| > |pwm_2|
#         # --- if system is turning left instead, then make the right wheel faster
#         if abs(self.pwm_1) < abs(self.pwm_2):
#             self.pwm_1 = self.pwm_2 # faster a little bit
#             cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#             self.__send(cmd) # format and send to the driver
#             return
#         # --- if system is standstill, moving for/back
#         elif self.pwm_1 == self.pwm_2:
#             # --- standstill
#             if -STOP_PWM < self.pwm_1 < STOP_PWM : 
#                 if direction: # if moving forward
#                     self.pwm_1 = DEPART_PWM
#                 else: # if moving backward
#                     self.pwm_1 = -DEPART_PWM
#                 cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             # --- moving forward
#             elif self.pwm_1 > STOP_PWM :
#                 self.__turnright_fw(direction, accel)
#                 return
#             # --- moving backward
#             else : # self.pwm_1 < 0
#                 self.__turnright_bw(direction, accel)
#                 return
#         else: # if system is really turning right: abs(self.pwm_1) > abs(self.pwm_2)
#             if self.pwm_1 > self.pwm_2: # positive value
#                 self.__turnright_fw(direction, accel)
#                 return
#             else: # negative value
#                 self.__turnright_bw(direction, accel)
#                 return

#     def __turnleft_fw(self, direction, accel):
#         if direction: # if turn right in forward direction
#             if self.pwm_2 < self.MAX_PWM:
#                 if -DEPART_PWM < self.pwm_2 < DEPART_PWM:
#                     self.pwm_2 = DEPART_PWM
#                 else:
#                     self.pwm_2 += accel # faster a little bit
#                 cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             elif self.pwm_2 > self.MAX_PWM:
#                 self.pwm_2 = self.MAX_PWM # protection if real speed is higher than limit
#                 cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             else: # self.pwm_2 == self.MAX_PWM
#                 if self.pwm_1 == 0 or abs(self.pwm_1) == DEPART_PWM: # reached max turning limit
#                     return
#                 elif abs(self.pwm_1) < DEPART_PWM: # -DEPART_PWM < self.pwm_1 < DEPART_PWM, with no self.pwm_1 = 0
#                     if self.pwm_1 > 0:
#                         self.pwm_1 = DEPART_PWM  # set to be the limit
#                     else:
#                         self.pwm_1 = -DEPART_PWM  # set to be the limit
#                     cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     return
#                 else: # if pwm_1 can be reduced further
#                     self.pwm_1 -= accel  # slower a little the other motor
#                     cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     return
#         else: # if turn right in backward direction
#             self.release()
#             return
    
#     def __turnleft_bw(self, direction, accel):
#         if direction: # if turn right in forward direction
#             self.release()
#             return
#         else: # if turn right in backward direction
#             if self.pwm_2 > -self.MAX_PWM:
#                 if -DEPART_PWM < self.pwm_2 < DEPART_PWM:
#                     self.pwm_2 = -DEPART_PWM
#                 else:
#                     self.pwm_2 -= accel # faster a little bit
#                 cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             elif self.pwm_2 < -self.MAX_PWM:
#                 self.pwm_2 = -self.MAX_PWM # protection if real speed is higher than limit
#                 cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             else: # self.pwm_2 == -self.MAX_PWM
#                 if self.pwm_1 == 0 or abs(self.pwm_1) == DEPART_PWM: # reached max turning limit
#                     return
#                 elif abs(self.pwm_1) < DEPART_PWM: # -DEPART_PWM < self.pwm_1 < DEPART_PWM, with no self.pwm_1 = 0
#                     if self.pwm_1 > 0:
#                         self.pwm_1 = DEPART_PWM  # set to be the limit
#                     else:
#                         self.pwm_1 = -DEPART_PWM  # set to be the limit
#                     cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     return
#                 else: # if pwm_1 can be reduced further
#                     self.pwm_1 += accel  # slower a little the other motor
#                     cmd = "{N1 P" + str(self.pwm_1) + "}" # {N1 P500} - set speed for pwm
#                     self.__send(cmd) # format and send to the driver
#                     return
    
#     def turn_left(self, direction, accel): # turn left, so only one motor rotate at a time  |pwm_2| > |pwm_1|
#         # --- if system is turning left instead, then make the left wheel faster
#         if abs(self.pwm_2) < abs(self.pwm_1):
#             self.pwm_2 = self.pwm_1 # faster a little bit
#             cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#             self.__send(cmd) # format and send to the driver
#             return
#         # --- if system is standstill, moving for/back
#         elif self.pwm_1 == self.pwm_2:
#             # --- standstill
#             if self.pwm_2 is 0 : 
#                 if direction: # if moving forward
#                     self.pwm_2 = DEPART_PWM
#                 else: # if moving backward
#                     self.pwm_2 = -DEPART_PWM
#                 cmd = "{N2 P" + str(self.pwm_2) + "}" # {N1 P500} - set speed for pwm
#                 self.__send(cmd) # format and send to the driver
#                 return
#             # --- moving forward
#             elif self.pwm_2 > 0 :
#                 self.__turnleft_fw(direction, accel)
#                 return
#             # --- moving backward
#             else : # self.pwm_2 < 0
#                 self.__turnleft_bw(direction, accel)
#                 return
#         else: # if system is really turning right: abs(self.pwm_2) > abs(self.pwm_1)
#             if self.pwm_2 > self.pwm_1: # positive value
#                 self.__turnleft_fw(direction, accel)
#                 return
#             else: # negative value
#                 self.__turnleft_bw(direction, accel)
#                 return
