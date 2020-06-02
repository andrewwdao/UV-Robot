"""------------------------------------------------------------*-
  camera web app module for Raspberry Pi
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Miguel Grinberg 2011-2019
  version 1.00 - 11/04/2020
 --------------------------------------------------------------
 *  Server created for the purpose of camera control
 *
 --------------------------------------------------------------"""
from camera_pi import Camera # Raspberry Pi camera module (requires picamera package)
import os
from flask import Flask, render_template, Response


app = Flask(__name__)


@app.route('/')
def index():
    """Video control home page."""
    return render_template('index.html')


def gen(camera):
    """Video control generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video control route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
