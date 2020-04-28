"""------------------------------------------------------------*-
  Admin credential init module for Flask server
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
 
 --------------------------------------------------------------"""
from app.models import User
from app import db
u = User(username='admin')
u.set_password('MIS@2020')
db.session.add(u)
db.session.commit()
