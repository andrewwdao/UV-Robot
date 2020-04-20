#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi

apt-get update
apt-get upgrade -y

# WiringPi  ## http://wiringpi.com/
apt-get install wiringpi -y

echo
echo
echo "Done."

## (c) 2020 Minh-An Dao. All right reserved