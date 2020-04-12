"""------------------------------------------------------------*-
  Init module for Flask server
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 11/04/2020
 --------------------------------------------------------------
 * Server created for the purpose of streaming video
 * Make the server a fully functional package
 *
 --------------------------------------------------------------"""
from flask import Flask, url_for
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
import logging
import os
import subprocess as subpro
import time

# LOGGING_DIR = '/tmp/MIS_logs'
LOGGING_DIR = './logs'

streaming_app = Flask(__name__)
streaming_app.config.from_object(Config)
db = SQLAlchemy(streaming_app)
migrate = Migrate(streaming_app, db)
bootstrap = Bootstrap(streaming_app)
streaming_app.config['BOOTSTRAP_SERVE_LOCAL'] = True  # make bootstrap use local resources instead of using online resources
login = LoginManager(streaming_app)
login.login_view = 'login'

from app.errors import bp as errors_bp
streaming_app.register_blueprint(errors_bp)

from app.streaming import bp as streaming_bp
streaming_app.register_blueprint(streaming_bp)

if not streaming_app.debug:  # move it to tmp folder for read-only system
    if not os.path.exists(LOGGING_DIR): 
        os.mkdir(LOGGING_DIR) # move it to tmp folder for read-only system
    file_handler = RotatingFileHandler(LOGGING_DIR + '/error.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.ERROR) # DEBUG, INFO, WARNING, ERROR and CRITICAL
    streaming_app.logger.addHandler(file_handler)

    streaming_app.logger.setLevel(logging.ERROR) # DEBUG, INFO, WARNING, ERROR and CRITICAL
    streaming_app.logger.info('System startup')


from app import models
