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
# RELAY_L1 = 4  # BCM mode
RELAY_L1 = 14  # BCM mode
RELAY_L2 = 17 # BCM mode
RELAY_R1 = 27 # BCM mode
RELAY_R2 = 22 # BCM mode

PWM_STEP = 10 # accel must be multiple of PWM_STEP = 10
ACCEL = 150 #ms
SAFETY_TIME = 500 #ms --> 1s
DANGER_FLAG = False

millis = lambda: int(time.time() * 1000)
# --------------------------- Set Up ----------------------------------------
# start to count time
U_watchdog = D_watchdog = L_watchdog = R_watchdog = millis() # monitoring interval for arrow buttons
STOP_millis = millis() # time flag to trigger auto stop

L1_watchdog = L2_watchdog = R1_watchdog = R2_watchdog = millis() # monitoring interval for L, R buttons
L1_FLAG = L2_FLAG = R1_FLAG = R2_FLAG = True

# server initialize
server = WebServer()

# =================================== motor control =============================================
def motor_controller():
    global DANGER_FLAG, STOP_millis, U_watchdog, D_watchdog, L_watchdog, R_watchdog
    
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


    # ================== Safety control ==================
    if (DANGER_FLAG) & ((millis() - STOP_millis) > SAFETY_TIME): # if time flag isn't gotten reset, then stop
        print('Motor stop')
        Motor.release()
        DANGER_FLAG = False

# =================================== admin command =============================================
def cmd_update():
    if ps2.cmdPressing():
         # --- START - turn off all relays
        if ps2.pressed(ps2.START):
            print('START pressed')
            GPIO.output(RELAY_L1, GPIO.HIGH) # turn off the relay
            GPIO.output(RELAY_L2, GPIO.HIGH) # turn off the relay
            GPIO.output(RELAY_R1, GPIO.HIGH) # turn off the relay
            GPIO.output(RELAY_R2, GPIO.HIGH) # turn off the relay
        # --- TRIANGLE - high speed
        if ps2.pressed(ps2.TRIANGLE):
            print('TRIANGLE pressed')
            Motor.MAX_PWM = 400
        # --- CROSS - low speed
        if ps2.pressed(ps2.CROSS):
            print('CROSS pressed')
            Motor.MAX_PWM = 200

# =================================== relay module =============================================
def relay_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_L1, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RELAY_L2, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RELAY_R1, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(RELAY_R2, GPIO.OUT, initial=GPIO.HIGH)

def __relay_toggle(FLAG, watchdog, button, RELAY):
    if ps2.pressed(button):
        print('pressed')
        watchdog = millis() # for recalculating interval
    elif ps2.isPressing(button) & ((millis() - watchdog) > SAFETY_TIME*2) & FLAG:
        print('toggled')
        if GPIO.input(RELAY):
            GPIO.output(RELAY, GPIO.LOW) # turn on the relay
        else:
            GPIO.output(RELAY, GPIO.HIGH) # turn off the relay
        FLAG = False
    return [FLAG, watchdog]

def relay_controller():
    global L1_watchdog, L2_watchdog, R1_watchdog, R2_watchdog, L1_FLAG, L2_FLAG, R1_FLAG, R2_FLAG
    
    if ps2.released(ps2.L1):
        print('L1 released')
        L1_FLAG = True # reset flag for next use
    if ps2.released(ps2.L2):
        print('L2 released')
        L2_FLAG = True # reset flag for next use
    if ps2.released(ps2.R1):
        print('R1 released')
        R1_FLAG = True # reset flag for next use
    if ps2.released(ps2.R2):
        print('R2 released')
        R2_FLAG = True # reset flag for next use

    if ps2.LRpressing():
        # --- L1
        [L1_FLAG, L1_watchdog] = __relay_toggle(L1_FLAG, L1_watchdog, ps2.L1, RELAY_L1)
        # --- L2
        [L2_FLAG, L2_watchdog] = __relay_toggle(L2_FLAG, L2_watchdog, ps2.L2, RELAY_L2)
        # --- R1
        [R1_FLAG, R1_watchdog] = __relay_toggle(R1_FLAG, R1_watchdog, ps2.R1, RELAY_R1)
        # --- R2
        [R2_FLAG, R2_watchdog] = __relay_toggle(R2_FLAG, R2_watchdog, ps2.R2, RELAY_R2)
# =================================================================================================


def main():  # Main program block
    relay_init()
    server.start()

    # forever loop start...
    while True:
        ps2.update()

        cmd_update()
        motor_controller()
        relay_controller()



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
        



        # if ps2.pressed(ps2.L1):
        #     print('L1 pressed')
        #     L1_watchdog = millis() # for recalculating interval
        # elif ps2.isPressing(ps2.L1) & ((millis() - L1_watchdog) > SAFETY_TIME*2) & L1_FLAG:
        #     print('L1 pressing')
        #     if GPIO.input(RELAY_L1):
        #         GPIO.output(RELAY_L1, GPIO.LOW) # turn on the relay
        #     else:
        #         GPIO.output(RELAY_L1, GPIO.HIGH) # turn off the relay
        #     L1_FLAG = False

        
        # if ps2.pressed(ps2.L2):
        #     print('L2 pressed')
        #     L2_watchdog = millis() # for recalculating interval
        # elif ps2.isPressing(ps2.L2) & ((millis() - L2_watchdog) > SAFETY_TIME*2) & L2_FLAG:
        #     print('L2 pressing')
        #     if GPIO.input(RELAY_L2):
        #         GPIO.output(RELAY_L2, GPIO.LOW) # turn on the relay
        #     else:
        #         GPIO.output(RELAY_L2, GPIO.HIGH) # turn off the relay
        #     L2_FLAG = False

        # if ps2.pressed(ps2.R1):
        #     print('R1 pressed')
        #     R1_watchdog = millis() # for recalculating interval
        # elif ps2.isPressing(ps2.R1) & ((millis() - R1_watchdog) > SAFETY_TIME*2) & R1_FLAG:
        #     print('R1 pressing')
        #     if GPIO.input(RELAY_R1):
        #         GPIO.output(RELAY_R1, GPIO.LOW) # turn on the relay
        #     else:
        #         GPIO.output(RELAY_R1, GPIO.HIGH) # turn off the relay
        #     R1_FLAG = False

        # if ps2.pressed(ps2.R2):
        #     print('R2 pressed')
        #     R2_watchdog = millis() # for recalculating interval
        # elif ps2.isPressing(ps2.R2) & ((millis() - R2_watchdog) > SAFETY_TIME*2) & R2_FLAG:
        #     print('R2 pressing')
        #     if GPIO.input(RELAY_R2):
        #         GPIO.output(RELAY_R2, GPIO.LOW) # turn on the relay
        #     else:
        #         GPIO.output(RELAY_R2, GPIO.HIGH) # turn off the relay
        #     R2_FLAG = False
