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
# import subprocess as sp
# from ps2x.streamReader import StreamReader
from app import streaming_app, socket
from flask_socketio import emit
# import sys
# import time
# import threading
# import signal
# import os

@socket.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})
    print('connected')

@socket.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socket.on('my event')
def hello():
    print("ABC")


if __name__ == "__main__":
    # streaming_app.run(host='0.0.0.0', port=7497, debug=False)  # run collecting app
    socket.run(streaming_app,host='0.0.0.0', port=8001)

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
