#!/usr/bin/env python3
"""------------------------------------------------------------*-
  Controller server module for UV Robot
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Anh-Khoi Tran 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 28/04/2020
 --------------------------------------------------------------
 * Server created for the purpose of control the robot from webserver
 * Make the server a fully functional package
 *
 * ref:
 * - https://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent
 * - https://blog.miguelgrinberg.com/post/flask-socketio-and-the-user-session
 
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
        emit('light', 'OF')

    if SPEED_STATE:
        emit('speed', 'HI')
    else:
        emit('speed', 'LO')

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
        sys.stdout.write("LO\n") # LIGHT ON
        emit('light', 'ON')
    else:
        sys.stdout.write("LF\n") # LIGHT OFF
        emit('light', 'OF')
    sys.stdout.flush()

@socket.on('speed')
def handle_speed_toggle():
    global SPEED_STATE
    
    SPEED_STATE = ~SPEED_STATE

    if SPEED_STATE:
        sys.stdout.write("HS\n") # HIGHSPEED
        emit('speed', 'HI')
    else:
        sys.stdout.write("LS\n") # LOWSPEED
        emit('speed', 'LO')

    sys.stdout.flush()


if __name__ == "__main__":
    # control_app.run(host='0.0.0.0', port=7497, debug=False)  # run collecting app
    socket.run(control_app,host='0.0.0.0', port=8003)
