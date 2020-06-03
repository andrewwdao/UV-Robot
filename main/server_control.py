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
from app import control_app, socket
from flask_socketio import emit
import sys

# L_DIR = "/tmp/MIS_logs/light"
LIGHT_STATE = False
SPEED_STATE = False

@socket.on('connect')
def test_connect():
    global LIGHT_STATE
    global SPEED_STATE

    sys.stdout.write("Client connected!\n")
    sys.stdout.flush()

    if LIGHT_STATE:
        emit('light', 'ON')
    else:
        emit('light', 'OFF')

    if SPEED_STATE:
        emit('speed', 'HIGH')
    else:
        emit('speed', 'LOW')

    # try:
    #     with open(L_DIR, "r") as f:
    #         emit('light', f.read() == 'ON')
    # except FileNotFoundError:
    #     sys.stdout.write(L_DIR + " not found!")
    #     sys.stdout.flush()

# @socket.on('pressed')
# def handle_key_pressed(signal):
#     sys.stdout.write(signal + "\n")
    # sys.stdout.flush()

@socket.on('pressed')
def handle_key_is_pressing(signal):
    sys.stdout.write(signal + "\n")
    sys.stdout.flush()

# @socket.on('released')
# def handle_key_released(signal):
#     sys.stdout.write(signal + "\n")
#     sys.stdout.flush()

@socket.on('light')
def handle_light_toggle():
    global LIGHT_STATE
    
    LIGHT_STATE = ~LIGHT_STATE

    if LIGHT_STATE:
        sys.stdout.write("LIGHT ON\n")
        emit('light', 'ON')
    else:
        sys.stdout.write("LIGHT OFF\n")
        emit('light', 'OFF')
    sys.stdout.flush()

@socket.on('speed')
def handle_speed_toggle():
    global SPEED_STATE
    
    SPEED_STATE = ~SPEED_STATE
    
    if SPEED_STATE:
        sys.stdout.write("HIGHSPEED\n")
        emit('speed', 'HIGH')
    else:
        sys.stdout.write("LOWSPEED\n")
        emit('speed', 'LOW')

    sys.stdout.flush()


if __name__ == "__main__":
    # control_app.run(host='0.0.0.0', port=7497, debug=False)  # run collecting app
    socket.run(control_app,host='0.0.0.0', port=8003)
