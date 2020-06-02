"""------------------------------------------------------------*-
  Init module for Flask server
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 11/04/2020
 --------------------------------------------------------------
 * Server created for the purpose of control video
 * Make the server a fully functional package
 *
 * ref:
 * - https://blog.miguelgrinberg.com/post/video-control-with-flask
 * - https://blog.miguelgrinberg.com/post/flask-video-control-revisited
 * - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database
 
 --------------------------------------------------------------"""
from flask import Flask, url_for, session, g
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
import logging
import os
import subprocess as subpro
import time
from datetime import timedelta

LOGGING_DIR = '/tmp/MIS_logs'
# LOGGING_DIR = './logs'

control_app = Flask(__name__)
control_app.config.from_object(Config)
db = SQLAlchemy(control_app)
migrate = Migrate(control_app, db)
bootstrap = Bootstrap(control_app)
control_app.config['BOOTSTRAP_SERVE_LOCAL'] = True  # make bootstrap use local resources instead of using online resources
login = LoginManager(control_app)
login.login_view = 'login' # The name of the view to redirect to when the user needs to log in. 
login.refresh_view = 'login' # The name of the view to redirect to when the user needs to reauthenticate.


from app.errors import bp as errors_bp
control_app.register_blueprint(errors_bp)

from app.control import bp as streaming_bp
control_app.register_blueprint(streaming_bp)

if not control_app.debug:  # move it to tmp folder for read-only system
    if not os.path.exists(LOGGING_DIR): 
        os.mkdir(LOGGING_DIR) # move it to tmp folder for read-only system
    file_handler = RotatingFileHandler(LOGGING_DIR + '/error.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.WARNING) # DEBUG, INFO, WARNING, ERROR and CRITICAL
    control_app.logger.addHandler(file_handler)

    control_app.logger.setLevel(logging.WARNING) # DEBUG, INFO, WARNING, ERROR and CRITICAL
    control_app.logger.info('System startup')


from app import models
