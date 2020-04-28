#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi

echo "This will set up the streaming server's prequisites for Raspberry Pi camera"

# workaround for automatically calling from main shell script
if ! [ "${1-install}" == "ignore" ] ; then

	apt-get update
	apt-get upgrade -y

	# pip installation
	apt-get install python3-pip -y

fi


# Pi Camera -- https://pypi.org/project/picamera/
pip3 install picamera

# Flask - WTForm - SQLAlchemy - Migrate - Bootstrap - Login  ## https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
pip3 install flask
pip3 install python-dotenv
pip3 install flask-wtf
pip3 install flask-sqlalchemy
pip3 install flask-migrate
pip3 install flask-bootstrap
pip3 install flask-login
# Gevent networking platform to deploy production server - https://pypi.org/project/gevent/#downloads
pip3 install gevent

# setup server database for admin login
chmod +x server-db_setup.sh
./server-db_setup.sh

echo
echo
echo "Server Done."

## (c) 2020 Minh-An Dao. All right reserved