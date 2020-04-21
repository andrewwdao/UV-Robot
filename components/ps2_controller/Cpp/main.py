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
    ps2.update()
    if ps2.buttonChanged():
      if ps2.pressed(ps2.UP):
        print('UP pressed')
      elif ps2.released(ps2.UP):
        print('UP released')
      
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

      if ps2.pressed(ps2.TRIANGLE):
        print('TRIANGLE pressed')
      elif ps2.released(ps2.TRIANGLE):
        print('TRIANGLE released')
      
      if ps2.pressed(ps2.CIRCLE):
        print('CIRCLE pressed')
      elif ps2.released(ps2.CIRCLE):
        print('CIRCLE released')
      
      if ps2.pressed(ps2.CROSS):
        print('CROSS pressed')
      elif ps2.released(ps2.CROSS):
        print('CROSS released')
      
      if ps2.pressed(ps2.SQUARE):
        print('SQUARE pressed')
      elif ps2.released(ps2.SQUARE):
        print('SQUARE released')
      
      if ps2.pressed(ps2.L1):
        print('L1 pressed')
      elif ps2.released(ps2.L1):
        print('L1 released')
      
      if ps2.pressed(ps2.L2):
        print('L2 pressed')
      elif ps2.released(ps2.L2):
        print('L2 released')
      
      if ps2.pressed(ps2.L3):
        print('L3 pressed')
      elif ps2.released(ps2.L3):
        print('L3 released')
      
      if ps2.pressed(ps2.R1):
        print('R1 pressed')
      elif ps2.released(ps2.R1):
        print('R1 released')
      
      if ps2.pressed(ps2.R2):
        print('R2 pressed')
      elif ps2.released(ps2.R2):
        print('R2 released')
      
      if ps2.pressed(ps2.R3):
        print('R3 pressed')
      elif ps2.released(ps2.R3):
        print('R3 released')
      
      if ps2.pressed(ps2.SELECT):
        print('SELECT pressed')
      elif ps2.released(ps2.SELECT):
        print('SELECT released')
      
      if ps2.pressed(ps2.START):
        print('START pressed')
      elif ps2.released(ps2.START):
        print('START released')
    
    if ps2.Lstickchanged():
      print(ps2.LstickRead())
        
except KeyboardInterrupt:
  pass