"""------------------------------------------------------------*-
  Config module for Flask server and database
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2019
  (c) Miguel Grinberg 2018
  version 1.00 - 19/10/2019
 --------------------------------------------------------------
 *
 *
 --------------------------------------------------------------"""
import os
# basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32) # 'Dao_Minh_An_secret_password' - The key is secure enough, and each time you launch your system the key changes invalidating all sessions.

