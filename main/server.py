"""------------------------------------------------------------*-
  Application server module for Flask server
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 28/04/2020
 --------------------------------------------------------------
 * Server created for the purpose of streaming video
 * Make the server a fully functional package
 *
 * ref:
 * - https://blog.miguelgrinberg.com/post/video-streaming-with-flask
 * - https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited
 * - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
 * - https://stackoverflow.com/questions/18277048/gevent-pywsgi-graceful-shutdown
 
 --------------------------------------------------------------"""
# from gevent.pywsgi import WSGIServer
# import gevent
import subprocess as sp
from ps2x.streamReader import StreamReader
import sys
import time
# import threading
# import signal
# import os

class WebServer(object):
    """
    A python written module for interacting with the server.

    """
    def __init__(self):
        self.TARGET = 'server_call.py' # absolute directory
        try:
            self.svobj = sp.Popen(['sudo','python3',self.TARGET],
                                                    shell=False,
                                                    stdout=sp.PIPE)
        except Exception as e:
            print(e)
            raise ValueError("Something went wrong on the server side")
        
        self.output  = StreamReader(self.svobj.stdout)
        print("Web server ready!")
        # value for the buttons and sticks
        self.buttons = None # all button released
        self.last_buttons = None # all button released

    def update(self):
        output = self.output.readline(0.05)  # 0.05 secs = 10ms to let the shell output the result
        if output:  # turn it into string if it is not a null
            self.last_buttons = self.buttons
            self.buttons = output.strip().decode("utf-8")
            print(self.buttons)
            return
        self.buttons = None
        return

    def shutdown(self):
        # check if process terminated or not
        # A None value indicates that the process hasn't terminated yet.
        if self.svobj.poll() is None:
            self.svobj.terminate()
            self.svobj.kill()
            print('Web Server terminated!')
    
    def buttonChanged(self): # will be TRUE if any button changes state (on to off, or off to on)
        return self.last_buttons != self.buttons
    
    def isPressing(self, button): # will be TRUE as long as a specific button is pressed
        return self.buttons == button
    
    def pressed(self, button): # will be true only once when button is pressed
        return self.buttonChanged() & self.isPressing(button)

    # released must be place independently, not hybrid under a pressing method!  
    def released(self, button): # will be true only once when button is released
        return self.buttonChanged() & (self.last_buttons == button)
    
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

# # ======================== for development only =====================
# def start():
#     # streaming_app.run(host='0.0.0.0', port=7497, debug=False)  # run collecting app
#     socket.run(streaming_app,host='0.0.0.0', port=7497)
# # ===================================================================

# ========================== for production =========================
# class WebServer(threading.Thread):
#     def __init__(self):
#         super().__init__()
#         self.pid = os.getpid()
        
#     def run(self):
#         self.server = WSGIServer(('0.0.0.0', 80), streaming_app)
#         self.gevent_signal = gevent.hub.signal(signal.SIGTERM, self.shutdown)
#         self.server.serve_forever()

#     # ======================== for development only =====================
#     # def run(self):
#     #     streaming_app.run(host='0.0.0.0', port=7497, debug=False)  # run collecting app
#     # ===================================================================

#     # call this is enough to kill the server, if you need to have a shutdown button on the web, then you need to open routes.py
#     def shutdown(self): # SIGINT or SIGTERM doesn't really matter since what shutdown server stays here
#         print(f'Shutting down server...\n')
#         self.server.stop()
#         self.server.close()
#         self.gevent_signal.cancel()
        

    # def start(self): --> existed already from parent 
