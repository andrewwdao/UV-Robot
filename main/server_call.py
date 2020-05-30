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
from app import streaming_app, socket
from flask_socketio import emit
import sys

@socket.on('connect')
def test_connect():
    sys.stdout.write("Client connected!\n")
    sys.stdout.flush()

@socket.on('key pressed')
def handle_key_pressed(signal):
    sys.stdout.write(signal + "\n")
    sys.stdout.flush()



if __name__ == "__main__":
    # streaming_app.run(host='0.0.0.0', port=7497, debug=False)  # run collecting app
    socket.run(streaming_app,host='0.0.0.0', port=8002)
