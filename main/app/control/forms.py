"""------------------------------------------------------------*-
  Form module for Flask server
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2019
  (c) Miguel Grinberg 2018
  version 1.00 - 19/10/2019
 --------------------------------------------------------------
 *  Define the form for flask server to collect.
 *
 --------------------------------------------------------------"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username: ', validators=[DataRequired()])
    password = StringField('Password: ', validators=[DataRequired()])
    submit = SubmitField('Sign in')
