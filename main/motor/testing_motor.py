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
from math import pi, sin

################# constant for PID #######################


__serial = serial.Serial(port='/dev/ttyUSB0',
                         baudrate=1000000,
                         bytesize=serial.EIGHTBITS, 
                         timeout=2
                          )

if __serial.isOpen():
    __serial.close()

__serial.open()

starter_cmd = "{N0 M2 A2000 R}" # Set all motors to PID mode, with Acceleration = 2000, reset position --> will also make all motors stop
starter_cmd = starter_cmd.encode('utf-8')
__serial.write(starter_cmd)
pos = 0
speed = 0
# pos_2 = 0
# speed_2 = 0
time.sleep(1)
starter_cmd = "{N0 P1000 V300}" # Set all motors to PID mode, with Acceleration = 2000, reset position --> will also make all motors stop
starter_cmd = starter_cmd.encode('utf-8')
__serial.write(starter_cmd)
time.sleep(1)
starter_cmd = "{N0 R}" # Set all motors to PID mode, with Acceleration = 2000, reset position --> will also make all motors stop
starter_cmd = starter_cmd.encode('utf-8')
__serial.write(starter_cmd)

ACCEL_TIME = 5
DUTY_CYCLE = 0.005 # 4kHz
alpha = 0
MAX_SPEED = 300
RAD_STEP = pi/2*DUTY_CYCLE/ACCEL_TIME
time.sleep(1)
print('running...')
for x in range(0, 100000):
    if alpha < pi/2:
        alpha += RAD_STEP
    pos = 54*pi*sin(alpha)
    # speed = MAX_SPEED*sin(alpha)
    speed = 200
    cmd = "{N0 P" + str(round(pos,3)) + " V" + str(round(speed, 3)) + "}" # {N1 P500 V100} - set position and speed for PID
    cmd = cmd.encode('utf-8')
    __serial.write(cmd) # send to the driver
    time.sleep(DUTY_CYCLE)  # sleep for 4us --> 250kHz
    print(str(round(speed, 3)))

# ACCEL_TIME = 3
# DUTY_CYCLE = 0.001 # 1kHz
# rad = 0
# MAX_SPEED = 300
# RAD_STEP = (pi/2)/(1/DUTY_CYCLE)/ACCEL_TIME

# print('running...')
# for x in range(0, 7000):
#     if rad < pi/2:
#         rad += RAD_STEP
#     pos += 1*sin(rad)
#     cmd = "{N0 P" + str(round(pos,2)) + " V" + str(MAX_SPEED) + "}" # {N1 P500 V100} - set position and speed for PID
#     cmd = cmd.encode('utf-8')
#     __serial.write(cmd) # send to the driver
#     time.sleep(DUTY_CYCLE)  # sleep for 4us --> 250kHz
#     print(str(round(pos, 2)))