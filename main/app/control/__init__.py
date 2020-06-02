"""------------------------------------------------------------*-
  Init module for Flask server
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2019
  (c) Miguel Grinberg 2018
  version 1.00 - 11/04/2020
 --------------------------------------------------------------
 * Make the server a fully functional package
 *
 --------------------------------------------------------------"""
from flask import Blueprint

bp = Blueprint('control', __name__)

from app.control import forms, routes
