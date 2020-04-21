"""------------------------------------------------------------*-
  Example of motor controlling for MIS-CTU UV robot
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  version 1.00 - 15/04/2020
 --------------------------------------------------------------
 *
 *
 --------------------------------------------------------------"""
from motor import Motor

PWM_STEP = 10 # accel must be multiple of PWM_STEP = 10

try:
  while True:
    data = input('What do you want to do?f/b/lf/lb/rf/rb/s: ')
    if data == 'f':
      Motor.move_fw(PWM_STEP)
    if data == 'b':
      Motor.move_bw(PWM_STEP)
    if data == 'lf':
      Motor.turn_left(Motor.FORWARD, PWM_STEP)
    if data == 'lb':
      Motor.turn_left(Motor.BACKWARD, PWM_STEP)
    if data == 'rf':
      Motor.turn_right(Motor.FORWARD, PWM_STEP)
    if data == 'rb':
      Motor.turn_right(Motor.BACKWARD, PWM_STEP)
    if data == 's':
      Motor.release()
except KeyboardInterrupt:
  pass