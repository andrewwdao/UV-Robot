"""------------------------------------------------------------*-
  Main Python file for the control Server.
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  (c) Miguel Grinberg 2018
  version 1.00 - 11/04/2020
 --------------------------------------------------------------
 *  Server created for the purpose of control video
 *
 --------------------------------------------------------------"""
from app import control_app, db
from app.models import User

@control_app.shell_context_processor
def make_shell_context():
  return {'db':db,'User':User}
