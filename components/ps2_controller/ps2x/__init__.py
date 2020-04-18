"""------------------------------------------------------------*-
  Init module for PS2X controller
  Tested on: Raspberry Pi 3B/3B+
  (c) Minh-An Dao 2020
  version 1.00 - 17/04/2020
 --------------------------------------------------------------
 * Module created for the purpose of receiving signal 
 * from the PS2X controller.
 *
 * Ported from Arduino-PS2X library (https://github.com/madsci1016/Arduino-PS2X)
 --------------------------------------------------------------"""
from ps2x.ps2x import PS2X

PS2_DAT = 4  # BCM mode
PS2_CMD = 17 # BCM mode
PS2_SEL = 27 # BCM mode
PS2_CLK = 22 # BCM mode
PS2_PRESSURE = True
PS2_RUMBLE = False

ps2 = PS2X(PS2_DAT, PS2_CMD, PS2_SEL, PS2_CLK, PS2_PRESSURE, PS2_RUMBLE)


