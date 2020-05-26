"""------------------------------------------------------------*-
  Main process for UVRobot
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2019 - 2020
  version 2.00 - 28/03/2020
 --------------------------------------------------------------
 *
 *
 --------------------------------------------------------------"""
from server import WebServer
from usb_peripherals import sensor, motor
from ps2x import ps2
import RPi.GPIO as GPIO
import subprocess as sp
import signal
import os
import time

# ---------------------------- Configurable parameters -------------------------
RELAY_01_PIN = 4  # BCM mode

L_LIMIT_UP_PIN = 5 # bcm mode - WARNING
L_LIMIT_DOWN_PIN = 6 # bcm mode - WARNING
R_LIMIT_UP_PIN = 19 # bcm mode - WARNING
R_LIMIT_DOWN_PIN = 26 # bcm mode - WARNING

# for pwm control
HIGH_SPEED = 600
LOW_SPEED = 200
PWM_STEP = 30 # accel must be multiple of PWM_STEP = 10
ACCEL = 50 # ms
SAFETY_TIME = 300 #ms --> 1s
DANGER_FLAG = False
FORWARD_FLAG = True # flag for turning, defaut in forward direction

millis = lambda: int(time.time() * 1000)
# --------------------------- Set Up ----------------------------------------
# start to count time
U_watchdog = D_watchdog = L_watchdog = R_watchdog = A_watchdog = millis() # monitoring interval for arrow buttons
STOP_millis = millis() # time flag to trigger auto stop

# L1_watchdog = L2_watchdog = R1_watchdog = R2_watchdog = millis() # monitoring interval for L, R buttons
# L1_FLAG = L2_FLAG = R1_FLAG = R2_FLAG = True
SQ_watchdog = millis() # monitor interval for SQUARE button
SQ_FLAG = True

MIN_HEIGHT = 30 #cm
LR_PRESS_FLAG = True
L_UL_FLAG = False # will be automatically updated to true
R_UL_FLAG = False # will be automatically updated to true


# server initialize
server = WebServer()

# =================================== admin command =============================================
def cmd_update():
    global SQ_watchdog, SQ_FLAG

    # ------------ Confirm release buttons ---------------------
    if ps2.released(ps2.SQUARE):
        print('SQUARE released')
        SQ_FLAG = True # reset flag for next use

    # ------------- Confirm pressing buttons -------------------
    if ps2.cmdPressing():
         # --- START - turn off all relays
        if ps2.pressed(ps2.START):
            print('START pressed - relays turned off')
            GPIO.output(RELAY_01_PIN, GPIO.HIGH) # turn off the relay
            
        # --- TRIANGLE - high speed
        if ps2.pressed(ps2.TRIANGLE):
            print('TRIANGLE pressed - high speed mode')
            motor.MAX_PWM = HIGH_SPEED
        # --- CROSS - low speed
        if ps2.pressed(ps2.CROSS):
            print('CROSS pressed - low speed mode')
            motor.MAX_PWM = LOW_SPEED
        # --- SQUARE - turn on UV lights
        if ps2.pressed(ps2.SQUARE):
            print('SQUARE pressed')
            SQ_watchdog = millis() # for recalculating interval
        elif ps2.isPressing(ps2.SQUARE) & ((millis() - SQ_watchdog) > SAFETY_TIME*2) & SQ_FLAG:
            print('relays toggled')
            if not GPIO.input(RELAY_01_PIN):
                GPIO.output(RELAY_01_PIN, GPIO.HIGH) # turn off the relay  
            else:
                GPIO.output(RELAY_01_PIN, GPIO.LOW) # turn on the relay
            SQ_FLAG = False

# =================================== motor control =============================================
def motor_controller():
    global DANGER_FLAG, FORWARD_FLAG, STOP_millis, U_watchdog, D_watchdog, L_watchdog, R_watchdog, A_watchdog
    
    # ================== Digital control ==================
    if ps2.arrowPressing():
        # --- UP
        if ps2.isPressing(ps2.UP) & ((millis() - U_watchdog) > ACCEL):
            print('UP pressed')
            motor.move_fw(PWM_STEP) # increasing algorithm integrated
            U_watchdog = millis() # for recalculating interval
            FORWARD_FLAG = True
        # --- DOWN
        if ps2.isPressing(ps2.DOWN) & ((millis() - D_watchdog) > ACCEL):
            print('DOWN pressed')
            motor.move_bw(PWM_STEP) # increasing algorithm integrated
            D_watchdog = millis() # for recalculating interval
            FORWARD_FLAG = False
        # --- LEFT
        if ps2.isPressing(ps2.LEFT) & ((millis() - L_watchdog) > ACCEL):
            print('LEFT pressed')
            motor.turn_left(FORWARD_FLAG,PWM_STEP) # increasing algorithm integrated
            L_watchdog = millis() # for recalculating interval
        # --- RIGHT
        if ps2.isPressing(ps2.RIGHT) & ((millis() - R_watchdog) > ACCEL):
            print('RIGHT pressed')
            motor.turn_right(FORWARD_FLAG,PWM_STEP) # increasing algorithm integrated
            R_watchdog = millis() # for recalculating interval
        # whether what arrow buttons are pressed, they created movement
        # so turn on dangerous flag for release motor mechanism 
        DANGER_FLAG = True
        STOP_millis = millis() # reset the flag so the motor won't stop
    # ================== Analog control ==================
    elif ps2.LstickTouched() & ((millis() - A_watchdog) > ACCEL):
        # print(ps2.LstickRead())
        [Lx, Ly] = ps2.LstickRead()
        if Ly < 127: # moving forward
            if Ly < 40:
                print('forward+++')
                motor.move_fw(PWM_STEP*2) # increasing algorithm integrated
            elif Ly < 80: # 40 < Ly < 80
                print('forward++')
                motor.move_fw(PWM_STEP) # increasing algorithm integrated
            else: # 80 < Ly < 127
                print('forward+')
                motor.move_fw(PWM_STEP/2) # increasing algorithm integrated
            FORWARD_FLAG = True
        elif Ly > 127: # moving backward
            if Ly > 210:
                print('backward+++')
                motor.move_bw(PWM_STEP*2) # increasing algorithm integrated
            elif Ly > 170: # 210 > Ly > 170
                print('backward++')
                motor.move_bw(PWM_STEP) # increasing algorithm integrated
            else: # 170 > Ly > 127
                print('backward+')
                motor.move_bw(PWM_STEP/2) # increasing algorithm integrated
            FORWARD_FLAG = False
        
        # for motor driver catching the information
        time.sleep(0.001)  # sleep for 1ms

        if Lx < 128: # turning left
            if Lx < 40:
                print('turn left+++')
                motor.turn_left(FORWARD_FLAG,PWM_STEP*2) # increasing algorithm integrated
            elif Lx < 80: # 40 < Lx < 80
                print('turn left++')
                motor.turn_left(FORWARD_FLAG,PWM_STEP) # increasing algorithm integrated
            else: # 80 < Lx < 127
                print('turn left+')
                motor.turn_left(FORWARD_FLAG,PWM_STEP/2) # increasing algorithm integrated
        elif Lx > 128: # turning right
            if Lx > 210:
                print('turn right+++')
                motor.turn_right(FORWARD_FLAG,PWM_STEP*2) # increasing algorithm integrated
            elif Lx > 170: # 210 > Lx > 170
                print('turn right++')
                motor.turn_right(FORWARD_FLAG,PWM_STEP) # increasing algorithm integrated
            else: # 170 > Lx > 127
                print('turn right+')
                motor.turn_right(FORWARD_FLAG,PWM_STEP/2) # increasing algorithm integrated

        #  turn on dangerous flag for release motor mechanism 
        DANGER_FLAG = True
        STOP_millis = A_watchdog = millis() # reset the flag so the motor won't stop
    

    # ================== Safety control ==================
    if (DANGER_FLAG) & ((millis() - STOP_millis) > SAFETY_TIME): # if time flag isn't gotten reset, then stop
        print('Releasing...')
        DANGER_FLAG = motor.release() # will only return False when stopped
        if not DANGER_FLAG:
            print('motor stopped!')

# =================================== init gpio, including relays =============================================
def gpio_init():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_01_PIN, GPIO.OUT, initial=GPIO.HIGH) # relay init
    GPIO.setup(L_LIMIT_UP_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP) # pulling up
    GPIO.setup(L_LIMIT_DOWN_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP) # pulling up
    GPIO.setup(R_LIMIT_UP_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP) # pulling up
    GPIO.setup(R_LIMIT_DOWN_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP) # pulling up
    
# other functions integrated inside cmd_update

# =================================== ultrasonic update =============================================
def ultrasonic_update():
    global L_UL_FLAG, R_UL_FLAG
    sensorval = sensor.read()
    # print(sensorval)

    # left hand ultrasonics sensor
    if int(sensorval[0]) > MIN_HEIGHT: # if sensor is greater than MIN_HEIGHT cm 
        L_UL_FLAG = True
    else: # sensor value < MIN_HEIGHT
        L_UL_FLAG = False
        motor.Lhand_stop() # motor stop

    # right hand ultrasonics sensor
    if int(sensorval[1]) > MIN_HEIGHT: # if sensor is greater than MIN_HEIGHT cm 
        R_UL_FLAG = True
    else: # sensor value < MIN_HEIGHT
        R_UL_FLAG = False
        motor.Rhand_stop() # motor stop

# =================================== hand command =============================================
def hand_controller():

    global LR_PRESS_FLAG
    # ------------ Confirm release buttons ---------------------
    if ((ps2.released(ps2.L1) or
       ps2.released(ps2.L2) or
       GPIO.input(L_LIMIT_UP_PIN)==GPIO.LOW or 
       GPIO.input(L_LIMIT_DOWN_PIN)==GPIO.LOW) and LR_PRESS_FLAG):
        print('Hand Released')
        LR_PRESS_FLAG = False
        motor.Lhand_stop() # motor stop
    if ((ps2.released(ps2.R1) or
       ps2.released(ps2.R2) or
       GPIO.input(R_LIMIT_UP_PIN)==GPIO.LOW or 
       GPIO.input(R_LIMIT_DOWN_PIN)==GPIO.LOW) and LR_PRESS_FLAG):
        print('Hand Released')
        LR_PRESS_FLAG = False
        motor.Rhand_stop() # motor stop

    # ------------- Confirm pressing buttons -------------------
    if ps2.LRpressing():
        LR_PRESS_FLAG = True
        # --- L1 pressed - Lhand move up
        if ps2.pressed(ps2.L1) and GPIO.input(L_LIMIT_UP_PIN)==GPIO.HIGH:
            print('L1 pressed - Lhand move up')
            motor.Lhand_up() # motor move up
            return
        # --- L2 pressed - Lhand move down
        if ps2.pressed(ps2.L2) and GPIO.input(L_LIMIT_DOWN_PIN)==GPIO.HIGH and L_UL_FLAG:
            print('L2 pressed - Lhand move down')
            motor.Lhand_down() # motor move down
            return
        
        # --- R1 pressed - Rhand move up
        if ps2.pressed(ps2.R1) and GPIO.input(R_LIMIT_UP_PIN)==GPIO.HIGH:
            print('R1 pressed - Rhand move up')
            motor.Rhand_up() # motor move up
            return
        # --- R2 pressed - Rhand move down
        if ps2.pressed(ps2.R2) and GPIO.input(R_LIMIT_DOWN_PIN)==GPIO.HIGH and R_UL_FLAG:
            print('R2 pressed - Rhand move down')
            motor.Rhand_down() # motor move down
            return

# =================================================================================================


def main():  # Main program block
    gpio_init()
    server.start()

    # forever loop start...
    while True:
        ps2.update()

        cmd_update()
        motor_controller()

        ultrasonic_update()
        hand_controller()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        print(e)
        GPIO.cleanup()
        ps2.clean()
        motor.clean()
        server.shutdown()
        # turn on ro
        sp.call(['sudo','mount','-o','remount,ro','/'], shell=False)
        sp.call(['sudo','mount','-o','remount,ro','/boot'], shell=False)
        
    except (OSError, Exception) as e: # I/O error or exception
        print(e)
        GPIO.cleanup()
        ps2.clean()
        motor.clean()
        server.shutdown()
        # turn on ro
        sp.call(['sudo','mount','-o','remount,ro','/'], shell=False)
        sp.call(['sudo','mount','-o','remount,ro','/boot'], shell=False)
        



# for pid control
# # PWM_STEP = 10 # accel must be multiple of PWM_STEP = 10
# STEP = 1
# SAFETY_TIME = 1500 #ms
# HOLD_TIME = 300 #ms
# DANGER_FLAG = False

# =================================== motor control =============================================
# def motor_controller():
#     global DANGER_FLAG, STOP_millis
    
#     # ================== Digital control ==================
#     if ps2.arrowPressing():
#         # --- UP
#         if ps2.isPressing(ps2.UP):
#             print('UP pressed')
#             motor.move_fw(STEP) # increasing algorithm integrated
#         # --- DOWN
#         if ps2.isPressing(ps2.DOWN):
#             print('DOWN pressed')
#             motor.move_bw(STEP) # increasing algorithm integrated
#         # --- LEFT
#         if ps2.isPressing(ps2.LEFT):
#             print('LEFT pressed')
#             motor.turn_left(motor.FORWARD,STEP) # increasing algorithm integrated
#         # --- RIGHT
#         if ps2.isPressing(ps2.RIGHT):
#             print('RIGHT pressed')
#             motor.turn_right(motor.FORWARD,STEP) # increasing algorithm integrated
#         # whether what arrow buttons are pressed, they created movement
#         # so turn on dangerous flag for release motor mechanism 
#         DANGER_FLAG = True
#         STOP_millis = millis() # reset the flag so the motor won't stop
#     # ================== Analog control ==================


#     # ================== Safety control ==================
#     elif DANGER_FLAG: # if time flag isn't gotten reset, then start releasing
#         print('motor releasing')
#         motor.release((millis() - STOP_millis) > HOLD_TIME, STEP)
#         if (millis() - STOP_millis) > SAFETY_TIME: # turn off when every has been settle
#             DANGER_FLAG = False


# # =================================== relay module =============================================
# def relay_init():
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(RELAY_L1, GPIO.OUT, initial=GPIO.HIGH)
#     GPIO.setup(RELAY_L2, GPIO.OUT, initial=GPIO.HIGH)
#     GPIO.setup(RELAY_R1, GPIO.OUT, initial=GPIO.HIGH)
#     GPIO.setup(RELAY_R2, GPIO.OUT, initial=GPIO.HIGH)

# def __relay_toggle(FLAG, watchdog, button, RELAY):
#     if ps2.pressed(button):
#         print('pressed')
#         watchdog = millis() # for recalculating interval
#     elif ps2.isPressing(button) & ((millis() - watchdog) > SAFETY_TIME*2) & FLAG:
#         print('toggled')
#         if GPIO.input(RELAY):
#             GPIO.output(RELAY, GPIO.LOW) # turn on the relay
#         else:
#             GPIO.output(RELAY, GPIO.HIGH) # turn off the relay
#         FLAG = False
#     return [FLAG, watchdog]

# def relay_controller():
#     global L1_watchdog, L2_watchdog, R1_watchdog, R2_watchdog, L1_FLAG, L2_FLAG, R1_FLAG, R2_FLAG
    
#     if ps2.released(ps2.L1):
#         print('L1 released')
#         L1_FLAG = True # reset flag for next use
#     if ps2.released(ps2.L2):
#         print('L2 released')
#         L2_FLAG = True # reset flag for next use
#     if ps2.released(ps2.R1):
#         print('R1 released')
#         R1_FLAG = True # reset flag for next use
#     if ps2.released(ps2.R2):
#         print('R2 released')
#         R2_FLAG = True # reset flag for next use

#     if ps2.LRpressing():
#         # --- L1
#         [L1_FLAG, L1_watchdog] = __relay_toggle(L1_FLAG, L1_watchdog, ps2.L1, RELAY_L1)
#         # --- L2
#         [L2_FLAG, L2_watchdog] = __relay_toggle(L2_FLAG, L2_watchdog, ps2.L2, RELAY_L2)
#         # --- R1
#         [R1_FLAG, R1_watchdog] = __relay_toggle(R1_FLAG, R1_watchdog, ps2.R1, RELAY_R1)
#         # --- R2
#         [R2_FLAG, R2_watchdog] = __relay_toggle(R2_FLAG, R2_watchdog, ps2.R2, RELAY_R2)
# =================================================================================================