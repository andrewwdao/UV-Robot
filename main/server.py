"""------------------------------------------------------------*-
  Full application server module for UV Robot
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Anh-Khoi Tran 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 03/06/2020
 --------------------------------------------------------------
 * Server created for the purpose of control and monitor the robot from webserver
 * Make the server a fully functional package
 *
 * ref:
 * - https://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent
 * - https://blog.miguelgrinberg.com/post/flask-socketio-and-the-user-session
 * - https://blog.miguelgrinberg.com/post/video-control-with-flask
 * - https://blog.miguelgrinberg.com/post/flask-video-control-revisited
 * - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
 * - https://stackoverflow.com/questions/18277048/gevent-pywsgi-graceful-shutdown
 
 --------------------------------------------------------------"""
import subprocess as sp
from ps2x.streamReader import StreamReader
from server_camera import CameraServer
import sys
import time

class WebServer(object):
    """
    A python written module for interacting with the server.

    """
    def __init__(self):
        self.TARGET = 'server_control.py' # absolute directory
        try:
            self.svobj = sp.Popen(['sudo','python3',self.TARGET],
                                                    shell=False,
                                                    stdout=sp.PIPE)
        except Exception as e:
            print(e)
            raise ValueError("Something went wrong on the server side")
        self.output  = StreamReader(self.svobj.stdout)

        self.camera = CameraServer()
        self.camera.start() #start camera server

        # Button constants
        self.UP         = 'UP'
        self.DOWN       = 'DO'
        self.LEFT       = 'LE'
        self.RIGHT      = 'RI'
        self.LHAND_UP   = 'LU'
        self.LHAND_DOWN = 'LD'
        self.RHAND_UP   = 'RU'
        self.RHAND_DOWN = 'RD'
        self.SPEED      = 'SP'
        self.TOGGLE     = 'TG'
        self.LIGHT_ON   = 'LO'
        self.LIGHT_OFF  = 'LF'
        self.HIGHSPEED  = 'HS'
        self.LOWSPEED   = 'LS'

        # value for the buttons and sticks
        self.buttons = None # all button released
        self.last_buttons = None # all button released

        print("Web server ready!")

    def update(self):
        output = self.output.readline(0.04)  # 0.04 secs = 40ms to let the shell output the result
        # sys.stdout.flush()
        # output = self.svobj.stdout.readline() # this will hang the system
        self.last_buttons = self.buttons
        if output:  # turn it into string if it is not a null
            self.buttons = output.strip().decode("utf-8")
            return
        self.buttons = None
        return

    def shutdown(self):
        # check if process terminated or not
        # A None value indicates that the process hasn't terminated yet.
        self.camera.shutdown()
        if self.svobj.poll() is None:
            self.svobj.terminate()
            self.svobj.kill()
            print('Web Server terminated!')
    
    def buttonChanged(self): # will be TRUE if any button changes state (on to off, or off to on)
        return self.last_buttons != self.buttons
    
    def buttonPressing(self): # will be TRUE as long as ANY button is pressed
        return self.buttons != None
    
    def arrowPressing(self): # will be TRUE as long as arrow buttons (UP, DOWN, RIGHT, LEFT) are pressed
        return self.buttons in [self.UP,self.DOWN,self.LEFT,self.RIGHT]
    
    def LRpressing(self): # will be TRUE as long as left right hand controlling buttons are pressed
        return self.buttons in [self.LHAND_UP,self.LHAND_DOWN,self.RHAND_UP,self.RHAND_DOWN]
    
    def isPressing(self, button): # will be TRUE as long as a specific button is pressed
        return self.buttons == button
    
    def pressed(self, button): # will be true only once when button is pressed
        return self.buttonChanged() and self.isPressing(button)

    # released must be place independently, not hybrid under a pressing method!  
    def released(self, button): # will be true only once when button is released
        return self.buttonChanged() and (self.last_buttons == button)
