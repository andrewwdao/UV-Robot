"""------------------------------------------------------------*-
  Main process for MISlocker
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2019 - 2020
  version 2.00 - 28/03/2020
 --------------------------------------------------------------
 *
 *
 --------------------------------------------------------------"""
import server
from motor import Motor
from ps2x import ps2
import time

# ---------------------------- Configurable parameters -------------------------
millis = lambda: int(time.time() * 1000)
# --------------------------- Set Up ----------------------------------------



def main():  # Main program block
    # ---------------------------- Configurable parameters -------------------------
    PWM_STEP = 10 # accel must be multiple of PWM_STEP = 10
    DANGER_FLAG = False
    ACCEL = 150 #ms
    SAFETY_TIME = 500 #ms --> 1s

    # start to count time
    last_millisU = millis() # monitoring interval
    last_millisD = last_millisL = last_millisR = last_millisU # multiple for arrow buttons
    STOP_millis = millis() # time flag to trigger auto stop
    
    # forever loop start...
    while True:
        ps2.update()

        # --- motor speed digital control
        if ps2.arrowPressing():
            UP_interval    = millis() - last_millisU # calculate interval
            DOWN_interval  = millis() - last_millisD # calculate interval
            LEFT_interval  = millis() - last_millisL # calculate interval
            RIGHT_interval = millis() - last_millisR # calculate interval

            # --- UP
            if ps2.isPressing(ps2.UP) & (UP_interval > ACCEL):
                print('UP pressed')
                Motor.move_fw(PWM_STEP) # increasing algorithm integrated
                last_millisU = millis() # for recalculating interval
                
            # --- DOWN
            if ps2.isPressing(ps2.DOWN) & (DOWN_interval > ACCEL):
                print('DOWN pressed')
                Motor.move_bw(PWM_STEP) # increasing algorithm integrated
                last_millisD = millis() # for recalculating interval
                
            # --- LEFT
            if ps2.isPressing(ps2.LEFT) & (LEFT_interval > ACCEL):
                print('LEFT pressed')
                Motor.turn_left(Motor.FORWARD,PWM_STEP) # increasing algorithm integrated
                last_millisL = millis() # for recalculating interval
                
            # --- RIGHT
            if ps2.isPressing(ps2.RIGHT) & (RIGHT_interval > ACCEL):
                print('RIGHT pressed')
                Motor.turn_right(Motor.FORWARD,PWM_STEP) # increasing algorithm integrated
                last_millisR = millis() # for recalculating interval
            
            # whether what arrow buttons are pressed, they created movement
            # so turn on dangerous flag for release motor mechanism 
            DANGER_FLAG = True
            STOP_millis = millis() # reset the flag so the motor won't stop
            
        if (DANGER_FLAG) & ((millis() - STOP_millis) > SAFETY_TIME): # if time flag isn't gotten reset, then stop
            print('Motor stop')
            Motor.release()
            DANGER_FLAG = False

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as e:
        print(e)
        # turn on ro
        # sp.call(['sudo','mount','-o','remount,ro','/'], shell=False)
        # sp.call(['sudo','mount','-o','remount,ro','/boot'], shell=False)
        
        # sp.Popen(['python3','syshalt.py'], shell=False) # closing procedure, included close off peripherals
        
    except (OSError, Exception) as e: # I/O error or exception
        print(e)
        # turn on ro
        # sp.call(['sudo','mount','-o','remount,ro','/'], shell=False)
        # sp.call(['sudo','mount','-o','remount,ro','/boot'], shell=False)
        