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
# import RPi.GPIO as GPIO
import sys

# RELAY_01_PIN = 4  # BCM mode
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(RELAY_01_PIN, GPIO.OUT, initial=GPIO.HIGH) # relay init

@socket.on('connect')
def test_connect():
    sys.stdout.write("Client connected!\n")
    sys.stdout.flush()

    try:
        with open("/tmp/MIS_logs/light", "r") as f:
            emit('light', f.read() == 'ON')
    except FileNotFoundError:
        sys.stdout.write("/tmp/MIS_logs/light not found!")
        sys.stdout.flush()

    # emit('light', not GPIO.input(RELAY_01_PIN))

# @socket.on('pressed')
# def handle_key_pressed(signal):
#     sys.stdout.write(signal + "\n")
    # sys.stdout.flush()

@socket.on('holding')
def handle_key_is_pressing(signal):
    sys.stdout.write(signal + "\n")
    sys.stdout.flush()

@socket.on('released')
def handle_key_released(signal):
    sys.stdout.write(signal + "\n")
    sys.stdout.flush()

@socket.on('light')
def handle_light_toggle():
    # if GPIO.input(RELAY_01_PIN):
    #     sys.stdout.write("LIGHT ON\n")
    #     emit('light', True)
    #     GPIO.output(RELAY_01_PIN, GPIO.LOW)
    # else:
    #     sys.stdout.write("LIGHT OFF\n")
    #     emit('light', False)
    #     GPIO.output(RELAY_01_PIN, GPIO.HIGH)
    # sys.stdout.flush()
    try:
        f = open("/tmp/MIS_logs/light", "r")
        state = (f.read() != 'ON')
        emit('light', state)
        f.close()

        with open("/tmp/MIS_logs", "w") as f:
            if state:
                f.write("ON")
            else:
                f.wrie("OFF")

    except FileNotFoundError:
        sys.stdout.write("/tmp/MIS_logs/light not found!")
        sys.stdout.flush()

if __name__ == "__main__":
    # streaming_app.run(host='0.0.0.0', port=7497, debug=False)  # run collecting app
    socket.run(streaming_app,host='0.0.0.0', port=8003)
