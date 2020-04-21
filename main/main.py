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
from datetime import datetime, timezone

# ---------------------------- Configurable parameters -------------------------

# --------------------------- Set Up ----------------------------------------



def main():  # Main program block
    # ---------------------------- Configurable parameters -------------------------
    PWM_STEP = 10 # accel must be multiple of PWM_STEP = 10
    UP_FLAG = False
    DOWN_FLAG = False
    LEFT_FLAG = False
    RIGHT_FLAG = False
    DANGER_FLAG = False
    ACCEL = 100000 #ms
    SAFETY_TIME = 1000000 #s

    # start to count time
    last_millisU = datetime.now(timezone.utc).microsecond
    STOP_millis = datetime.now(timezone.utc).microsecond # time flag to trigger auto stop
    print(last_millisU)
    print(STOP_millis)
    # forever loop start...
    while True:
        ps2.update()

        
        if ps2.buttonChanged():
            UP_interval = datetime.now(timezone.utc).microsecond - last_millisU # calculate interval
            print(UP_interval)
            if (ps2.pressed(ps2.UP) | UP_FLAG) & (UP_interval > ACCEL):
                print('UP pressed')
                Motor.move_fw(PWM_STEP) # increasing algorithm integrated
                UP_FLAG = True
                last_millisU = datetime.now(timezone.utc).microsecond # for recalculating interval
                DANGER_FLAG = True
                STOP_millis = datetime.now(timezone.utc).microsecond # reset the flag so the motor won't stop
            elif ps2.released(ps2.UP):
                print('UP released')
                UP_FLAG = False
            
            if ps2.pressed(ps2.DOWN):
                print('DOWN pressed')
            elif ps2.released(ps2.DOWN):
                print('DOWN released')
            
            if ps2.pressed(ps2.LEFT):
                print('LEFT pressed')
            elif ps2.released(ps2.LEFT):
                print('LEFT released')

            if ps2.pressed(ps2.RIGHT):
                print('RIGHT pressed')
            elif ps2.released(ps2.RIGHT):
                print('RIGHT released')

        if (DANGER_FLAG) & ((datetime.now(timezone.utc).microsecond - STOP_millis) > SAFETY_TIME): # if time flag isn't gotten reset, then stop
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
        