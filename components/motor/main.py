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

PWM_STEP = 20 # must be multiple of 10

try:
  while True:
    data = input('What do you want to do?f/b/l/r/s: ')
    if data == 'f':
      Motor.move_fw(PWM_STEP)
    if data == 'b':
      Motor.move_bw(PWM_STEP)
    if data == 'l':
      Motor.turn_left(PWM_STEP)
    if data == 'r':
      Motor.turn_right(PWM_STEP)
    if data == 's':
      Motor.release()
except KeyboardInterrupt:
  pass