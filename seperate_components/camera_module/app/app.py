"""------------------------------------------------------------*-
  Main Python file for the streaming Server.
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 11/04/2020
 --------------------------------------------------------------
 *  Server created for the purpose of streaming video
 *
 --------------------------------------------------------------"""
from app import streaming_app, db
from app.models import User

@streaming_app.shell_context_processor
def make_shell_context():
  return {'db':db,'User':User}
