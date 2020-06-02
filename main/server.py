"""------------------------------------------------------------*-
  Application server module for Flask server
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 28/04/2020
 --------------------------------------------------------------
 * Server created for the purpose of control video
 * Make the server a fully functional package
 *
 * ref:
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

        print("Web server ready!")
        # value for the buttons and sticks
        self.buttons = None # all button released
        self.last_buttons = None # all button released

    def update(self):
        output = self.output.readline(0.05)  # 0.05 secs = 10ms to let the shell output the result
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
    
    def isPressing(self, button): # will be TRUE as long as a specific button is pressed
        return self.buttons == button
    
    def pressed(self, button): # will be true only once when button is pressed
        return self.buttonChanged() and self.isPressing(button)

    # released must be place independently, not hybrid under a pressing method!  
    def released(self, button): # will be true only once when button is released
        return self.buttonChanged() and (self.last_buttons == button)
    
    # def isPressing(self):
    #     if self.buttons:
    #         return True
    #     return False
    
    # def isReleased(self, button):
    #     if self.buttons == button + "R":
    #         return True
    #     return False
    
    # def got_cmd(self):
    #     if self.buttons:
    #         return True
    #     return False
    
    # def lighton(self):
    #     self.pressed("LIGHT ON")
            
    
    # def lightoff(self):
    #     self.pressed("LIGHT OFF")

    # def set_lowspeed(self):
    #     self.pressed("LOWSPEED")
    
    # def set_highspeed(self):
    #     self.pressed("HIGHSPEED")
