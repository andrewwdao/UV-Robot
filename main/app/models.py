"""------------------------------------------------------------*-
  Model module for Flask server
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2019-2020
  (c) Miguel Grinberg 2018
  version 1.10 - 21/03/2020
 --------------------------------------------------------------
 * Defines database columns and tables
 *
 --------------------------------------------------------------"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from app import db, login
from datetime import datetime, timezone

class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  password_hash = db.Column(db.String(128))

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return '<User {} - {}>'.format(self.id, self.username)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
