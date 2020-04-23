"""------------------------------------------------------------*-
  Main process for MIS-CTU UV robot
  Tested on: Raspberry Pi 3 B+
  (c) Minh-An Dao 2020
  version 1.00 - 12/04/2020
 --------------------------------------------------------------
 *
 *
 --------------------------------------------------------------"""
# import server

# server.run()

from server import WebServer
server = WebServer()
server.start()
# use this if you want to wait for the server - server.join() # Wait until the server thread terminates -- this is a function from the parent class Thread

