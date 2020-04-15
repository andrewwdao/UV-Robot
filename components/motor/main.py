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

try:
  while True:
    data = input('What do you want to do?f/b/l/r/s')
    if data == 'f':
      Motor.move_fw(50)
    if data == 'b':
      Motor.move_bw(50)
    if data == 'l':
      Motor.turn_left(50)
    if data == 'r':
      Motor.turn_right(50)
    if data == 's':
      Motor.release()
except KeyboardInterrupt:
  pass