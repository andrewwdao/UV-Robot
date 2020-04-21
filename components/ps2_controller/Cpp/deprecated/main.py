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

try:
  while True:
    if ps2.changed():
      button_data = ps2.read()
      stick_data = ps2.readStick()
      if button_data is not None:
        print(button_data)
      if stick_data[0] is not None:
        print(stick_data)
        
except KeyboardInterrupt:
  pass