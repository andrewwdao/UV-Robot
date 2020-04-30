"""------------------------------------------------------------*-
  Main process for MISlocker
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2019 - 2020
  version 2.00 - 28/03/2020
 --------------------------------------------------------------
 *
 *
 --------------------------------------------------------------"""
from server import WebServer
from motor import Motor
from ps2x import ps2
import RPi.GPIO as GPIO
import subprocess as sp
import signal
import os
import time

# ---------------------------- Configurable parameters -------------------------
RELAY_01 = 4  # BCM mode
RELAY_02 = 17 # BCM mode
RELAY_03 = 27 # BCM mode
RELAY_04 = 22 # BCM mode

# for pwm control
HIGH_SPEED = 600
LOW_SPEED = 200
PWM_STEP = 20 # accel must be multiple of PWM_STEP = 10
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

# server initialize
server = WebServer()

# =================================== motor control =============================================
def motor_controller():
    global DANGER_FLAG, FORWARD_FLAG, STOP_millis, U_watchdog, D_watchdog, L_watchdog, R_watchdog, A_watchdog
    
    # ================== Digital control ==================
    if ps2.arrowPressing():
        # --- UP
        if ps2.isPressing(ps2.UP) & ((millis() - U_watchdog) > ACCEL):
            print('UP pressed')
            Motor.move_fw(PWM_STEP) # increasing algorithm integrated
            U_watchdog = millis() # for recalculating interval
        # --- DOWN
        if ps2.isPressing(ps2.DOWN) & ((millis() - D_watchdog) > ACCEL):
            print('DOWN pressed')
            Motor.move_bw(PWM_STEP) # increasing algorithm integrated
            D_watchdog = millis() # for recalculating interval
        # --- LEFT
        if ps2.isPressing(ps2.LEFT) & ((millis() - L_watchdog) > ACCEL):
            print('LEFT pressed')
            Motor.turn_left(Motor.FORWARD,PWM_STEP) # increasing algorithm integrated
            L_watchdog = millis() # for recalculating interval
        # --- RIGHT
        if ps2.isPressing(ps2.RIGHT) & ((millis() - R_watchdog) > ACCEL):
            print('RIGHT pressed')
            Motor.turn_right(Motor.FORWARD,PWM_STEP) # increasing algorithm integrated
            R_watchdog = millis() # for recalculating interval
        # whether what arrow buttons are pressed, they created movement
        # so turn on dangerous flag for release motor mechanism 
        DANGER_FLAG = True
        STOP_millis = millis() # reset the flag so the motor won't stop
    # ================== Analog control ==================
    elif (ps2.LstickRead() != [128, 127]) & ((millis() - A_watchdog) > ACCEL):
        [Lx, Ly] = ps2.LstickRead()
        if Ly < 127: # moving forward
            if Ly < 40:
                print('forward+++')
                Motor.move_fw(PWM_STEP*3) # increasing algorithm integrated
            elif Ly < 80: # 40 < Ly < 80
                print('forward++')
                Motor.move_fw(PWM_STEP*2) # increasing algorithm integrated
            else: # 80 < Ly < 127
                print('forward+')
                Motor.move_fw(PWM_STEP) # increasing algorithm integrated
            FORWARD_FLAG = True
        elif Ly > 127: # moving backward
            if Ly > 210:
                print('backward+++')
                Motor.move_bw(PWM_STEP*3) # increasing algorithm integrated
            elif Ly > 170: # 210 > Ly > 170
                print('backward++')
                Motor.move_bw(PWM_STEP*2) # increasing algorithm integrated
            else: # 170 > Ly > 127
                print('backward+')
                Motor.move_bw(PWM_STEP) # increasing algorithm integrated
            FORWARD_FLAG = False
        
        # for motor driver catching the information
        time.sleep(0.001)  # sleep for 1ms

        if Lx < 128: # turning left
            if Ly < 40:
                print('turn left+++')
                Motor.turn_left(FORWARD_FLAG,PWM_STEP*3) # increasing algorithm integrated
            elif Ly < 80: # 40 < Ly < 80
                print('turn left++')
                Motor.turn_left(FORWARD_FLAG,PWM_STEP*2) # increasing algorithm integrated
            else: # 80 < Ly < 127
                print('turn left+')
                Motor.turn_left(FORWARD_FLAG,PWM_STEP) # increasing algorithm integrated
        elif Lx > 128: # turning right
            if Ly > 210:
                print('turn right+++')
                Motor.turn_right(FORWARD_FLAG,PWM_STEP*3) # increasing algorithm integrated
            elif Ly > 170: # 210 > Ly > 170
                print('turn right++')
                Motor.turn_right(FORWARD_FLAG,PWM_STEP*2) # increasing algorithm integrated
            else: # 170 > Ly > 127
                print('turn right+')
                Motor.turn_right(FORWARD_FLAG,PWM_STEP) # increasing algorithm integrated

        #  turn on dangerous flag for release motor mechanism 
        DANGER_FLAG = True
        STOP_millis = A_watchdog = millis() # reset the flag so the motor won't stop
    

    # ================== Safety control ==================
    if (DANGER_FLAG) & ((millis() - STOP_millis) > SAFETY_TIME): # if time flag isn't gotten reset, then stop
        print('Releasing...')
        DANGER_FLAG = Motor.release() # will only return False when stopped
        if not DANGER_FLAG:
            print('Motor stopped!')
        
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
            GPIO.output(RELAY_01, GPIO.HIGH) # turn off the relay
            GPIO.output(RELAY_02, GPIO.HIGH) # turn off the relay
            GPIO.output(RELAY_03, GPIO.HIGH) # turn off the relay
            GPIO.output(RELAY_04, GPIO.HIGH) # turn off the relay
        # --- TRIANGLE - high speed
        if ps2.pressed(ps2.TRIANGLE):
            print('TRIANGLE pressed')
            Motor.MAX_PWM = HIGH_SPEED
        # --- CROSS - low speed
        if ps2.pressed(ps2.CROSS):
            print('CROSS pressed')
            Motor.MAX_PWM = LOW_SPEED
        # --- SQUARE - turn on UV lights
        if ps2.pressed(ps2.SQUARE):
            print('SQUARE pressed')
            SQ_watchdog = millis() # for recalculating interval
        elif ps2.isPressing(ps2.SQUARE) & ((millis() - SQ_watchdog) > SAFETY_TIME*2) & SQ_FLAG:
            print('relays toggled')
            if not (GPIO.input(RELAY_01) or GPIO.input(RELAY_02) or GPIO.input(RELAY_03) or GPIO.input(RELAY_04)):
                GPIO.output(RELAY_01, GPIO.HIGH) # turn off the relay
                GPIO.output(RELAY_02, GPIO.HIGH) # turn off the relay
                GPIO.output(RELAY_03, GPIO.HIGH) # turn off the relay
                GPIO.output(RELAY_04, GPIO.HIGH) # turn off the relay
            else:
                GPIO.output(RELAY_01, GPIO.LOW) # turn on the relay
                GPIO.output(RELAY_02, GPIO.LOW) # turn on the relay
                GPIO.output(RELAY_03, GPIO.LOW) # turn on the relay
                GPIO.output(RELAY_04, GPIO.LOW) # turn on the relay
            SQ_FLAG = False

# =================================== relay module =============================================
def relay_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_01, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RELAY_02, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RELAY_03, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RELAY_04, GPIO.OUT, initial=GPIO.HIGH)

# other functions integrated inside cmd_update
        
# =================================================================================================


def main():  # Main program block
    relay_init()
    server.start()

    # forever loop start...
    while True:
        ps2.update()

        cmd_update()
        motor_controller()
        



if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        print(e)
        GPIO.cleanup()
        ps2.clean()
        Motor.clean()
        server.shutdown()
        # turn on ro
        sp.call(['sudo','mount','-o','remount,ro','/'], shell=False)
        sp.call(['sudo','mount','-o','remount,ro','/boot'], shell=False)
        
    except (OSError, Exception) as e: # I/O error or exception
        print(e)
        GPIO.cleanup()
        ps2.clean()
        Motor.clean()
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
#             Motor.move_fw(STEP) # increasing algorithm integrated
#         # --- DOWN
#         if ps2.isPressing(ps2.DOWN):
#             print('DOWN pressed')
#             Motor.move_bw(STEP) # increasing algorithm integrated
#         # --- LEFT
#         if ps2.isPressing(ps2.LEFT):
#             print('LEFT pressed')
#             Motor.turn_left(Motor.FORWARD,STEP) # increasing algorithm integrated
#         # --- RIGHT
#         if ps2.isPressing(ps2.RIGHT):
#             print('RIGHT pressed')
#             Motor.turn_right(Motor.FORWARD,STEP) # increasing algorithm integrated
#         # whether what arrow buttons are pressed, they created movement
#         # so turn on dangerous flag for release motor mechanism 
#         DANGER_FLAG = True
#         STOP_millis = millis() # reset the flag so the motor won't stop
#     # ================== Analog control ==================


#     # ================== Safety control ==================
#     elif DANGER_FLAG: # if time flag isn't gotten reset, then start releasing
#         print('Motor releasing')
#         Motor.release((millis() - STOP_millis) > HOLD_TIME, STEP)
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