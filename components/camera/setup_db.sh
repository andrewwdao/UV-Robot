#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi

apt-get update 
apt-get upgrade -y

cd app

# delete old database (admin information)
if [ -f "./database.db" ] ; then # check if database.db exist or not
	rm -rf database.db
fi

# delete old migrations folder
if [ -d "./migrations" ] ; then  # check if the directory exist or not
	rm -rf migrations
fi

# delete old log folder in the app folder
if [ -d "./logs" ] ; then  # check if the directory exist or not
	rm -rf logs
fi


flask db init
flask db migrate -m "users table"
flask db upgrade

cd .. # return to main project folder

# delete old log again in the main folder
if [ -d "./logs" ] ; then  # check if the directory exist or not
	rm -rf logs
fi

python3 admin_init.py


## (c) 2020 Minh-An Dao. All right reserved