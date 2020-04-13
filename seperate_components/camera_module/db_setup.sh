#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi
cd app

flask db init
flask db migrate -m "users table"
flask db upgrade

cd ..

python3 admin_init.py
