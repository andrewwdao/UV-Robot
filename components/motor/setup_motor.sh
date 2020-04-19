#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi

apt-get update
apt-get upgrade -y

# Pyserial package install  ## https://pyserial.readthedocs.io/en/latest/shortintro.html#opening-serial-ports
apt-get install python3-serial -y
# check if the phrase "enable_uart=1" existed in the file or not
if [ 0 -eq $( grep -c 'enable_uart=1' /boot/config.txt ) ]; then
	echo "enable_uart=1" | tee -a /boot/config.txt
fi

# show all usb plugged in
ls /dev/serial/by-*


## (c) 2020 Minh-An Dao. All right reserved