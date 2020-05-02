"""------------------------------------------------------------*-
  Example of receiving signal from PS2 controller
  Tested on: Raspberry Pi 3 B/B+
  (c) Minh-An Dao 2020
  version 1.10 - 28/04/2020
 --------------------------------------------------------------
 *
 *
 --------------------------------------------------------------"""
from ps2x import ps2
import time

try:
  while True:
    ps2.update()

    # ------------ Confirm release buttons ---------------------
    if ps2.released(ps2.SQUARE):
      print('SQUARE released')


    # ------------- Confirm pressing buttons -------------------
    if ps2.buttonChanged(): # any button changes will trigger this
      if ps2.pressed(ps2.UP):  # will return True ONCE when button is pressed
        print('UP pressed')
      elif ps2.released(ps2.UP): # release works independently or inside buttonChanged flag, not any other flag
        print('UP released')
      # other arrow buttons...
      if ps2.pressed(ps2.TRIANGLE): # will return True ONCE when button is pressed
        print('TRIANGLE pressed')
      elif ps2.released(ps2.TRIANGLE): # release works independently or inside buttonChanged flag, not any other flag
        print('TRIANGLE released')
      # other command buttons...
      if ps2.pressed(ps2.L1): # will return True ONCE when button is pressed
        print('L1 pressed')
      elif ps2.released(ps2.L1): # release works independently or inside buttonChanged flag, not any other flag
        print('L1 released')
      # other LR buttons...
      


    # ------------- Confirm pressing Command buttons -------------------
    # release recognition must be place OUTSIDE
    if ps2.cmdPressing(): # including TRIANGLE, CIRCLE, CROSS, SQUARE, SELECT, START
      if ps2.isPressing(ps2.TRIANGLE): # will return True as long as button is pressing
        print('TRIANGLE is being pressed')
      if ps2.pressed(ps2.CIRCLE): # will return True ONCE when button is pressed
        print('CIRCLE pressed')
      if ps2.pressed(ps2.CROSS): # will return True ONCE when button is pressed
        print('CROSS pressed')
      if ps2.pressed(ps2.SQUARE): # will return True ONCE when button is pressed
        print('SQUARE pressed')
      if ps2.pressed(ps2.SELECT): # will return True ONCE when button is pressed
        print('SELECT pressed')
      if ps2.pressed(ps2.START): # will return True ONCE when button is pressed
        print('START pressed')
      
    # ------------- Confirm pressing arrow buttons -------------------
    # release recognition must be place OUTSIDE
    if ps2.arrowPressing(): # including UP, DOWN, LEFT, RIGHT
      if ps2.isPressing(ps2.UP): # will return True as long as button is pressing
        print('UP is being pressed')
      if ps2.pressed(ps2.DOWN): # will return True ONCE when button is pressed
        print('DOWN pressed')
      if ps2.pressed(ps2.LEFT): # will return True ONCE when button is pressed
        print('LEFT pressed')
      if ps2.pressed(ps2.RIGHT): # will return True ONCE when button is pressed
        print('RIGHT pressed')


    # ------------- Confirm pressing LR buttons -------------------
    # release recognition must be place OUTSIDE
    if ps2.LRpressing(): # including L1, L2, L3, R1, R2, R3
      if ps2.isPressing(ps2.L1): # will return True as long as button is pressing
        print('L1 is being pressed')
      if ps2.pressed(ps2.L2): # will return True ONCE when button is pressed
        print('L2 pressed')
      if ps2.pressed(ps2.L3): # will return True ONCE when button is pressed
        print('L3 pressed')
      if ps2.pressed(ps2.R1): # will return True ONCE when button is pressed
        print('R1 pressed')
      if ps2.pressed(ps2.R2): # will return True ONCE when button is pressed
        print('R2 pressed')
      if ps2.pressed(ps2.R3): # will return True ONCE when button is pressed
        print('R3 pressed')
      

      # ================== Analog monitoring ==================
    if ps2.LstickChanged(): # will triggered when Left stick is changing
      print(ps2.LstickRead())
    if (ps2.LstickTouched()): # will triggered when Left stick is out of stable position (may not changing though)
      [Lx, Ly] = ps2.LstickRead()
      # do something you want with Lx, Ly
      
except KeyboardInterrupt:
  pass