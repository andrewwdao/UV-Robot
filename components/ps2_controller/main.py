"""------------------------------------------------------------*-
  Example of receiving signal from PS2 controller for MIS-CTU UV robot
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  version 1.00 - 17/04/2020
 --------------------------------------------------------------
 *
 *
 --------------------------------------------------------------"""
from ps2x import ps2
import time
PWM_STEP = 20 # must be multiple of 10

try:
  while True:
    # time.sleep(0.05) # 50ms
    ps2.update()

    # if ps2.changed(): # check if any button is changed
    #   if ps2.pressed(ps2.START):
    #     print("Start is pressed once")
    # if ps2.pressed(ps2.START):
    #     print("Start is pressed once")
    # if ps2.isPressing(ps2.START):
    #     print("Start is pressing")

    if ps2.isPressing(ps2.UP):
      print("UP is pressing this hard: ", ps2.analogRead(ps2.UP))
    if ps2.isPressing(ps2.DOWN):
      print("DOWN is pressing this hard: ", ps2.analogRead(ps2.DOWN))
    if ps2.isPressing(ps2.RIGHT):
      print("RIGHT is pressing this hard: ", ps2.analogRead(ps2.RIGHT))
    if ps2.isPressing(ps2.LEFT):
      print("LEFT is pressing this hard: ", ps2.analogRead(ps2.LEFT))

except KeyboardInterrupt:
  pass