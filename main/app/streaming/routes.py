"""------------------------------------------------------------*-
  Route module for the streaming Server.
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 12/04/2020
 --------------------------------------------------------------
 *  html routes for functions of the server
 *
 --------------------------------------------------------------"""
from flask import render_template, flash, redirect, url_for, request, Response, session
from flask_login import current_user, login_user, login_required, logout_user
from app import streaming_app, db
from app.streaming.forms import LoginForm
from app.models import User
from app.camera_pi import Camera # Raspberry Pi camera module (requires picamera package)
# import os
# import signal
# import subprocess as subpro
from datetime import timedelta

# shutdown production server
# def shutdownServer():
#     print('Prepare to shutting down server...')
#     # we want to do this, but in a little delay, so do it in a separate thread
#     # os.kill(int(os.getpid()),signal.SIGTERM) # find out the current task it's running on, then kill it
#     subpro.Popen(['sudo','python3','shutdown-server.py',str(os.getpid())], shell=False) # send the pid of the current webserver and send signal to kill it
    

# ======================== for development only =====================
# def shutdownServer():
#     # Start shutting down server
#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()
# ===================================================================


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@streaming_app.route('/', methods=['GET', 'POST'])
@streaming_app.route('/index', methods=['GET', 'POST'])
@login_required
# @fresh_login_required
def index():
    
    templateData = {
        'server_title': 'MIS-CTU UV Robot', # title on browser
        'main_title': 'Disinfection Robot Controller',
    }

    """Video streaming home page."""
    return render_template('streaming/index.html', **templateData)


@streaming_app.route('/video_feed')
@login_required
# @fresh_login_required
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@streaming_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login')) # , duration = timedelta(seconds=5)
        login_user(user, remember = False) # only login 1 time - no remember
        return redirect(url_for('index'))

    templateData = {
        'server_title': 'MIS-CTU UV Robot', # title on browser
        'main_title': 'UV Disinfection Robot',
        'main_func': 'Login',
        'form': form
    }
    return render_template('streaming/login.html', **templateData)


@streaming_app.route('/about')
def about():
    return render_template('about.html')

@streaming_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
