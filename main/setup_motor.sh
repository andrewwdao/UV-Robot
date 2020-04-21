#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi

echo "This will set up the motor driver MSD_EM's prequisites for Raspberry Pi"

# workaround for automatically calling from main shell script
if ! [ "$1" == "ignore" ] ; then

	apt-get update
	apt-get upgrade -y

fi


# Pyserial package install  ## https://pyserial.readthedocs.io/en/latest/shortintro.html#opening-serial-ports
apt-get install python3-serial -y
# check if the phrase "enable_uart=1" existed in the file or not
if [ 0 -eq $( grep -c 'enable_uart=1' /boot/config.txt ) ]; then
	# if not exist this phrase, then add it
	echo "enable_uart=1" | tee -a /boot/config.txt
fi

# show all usb plugged in
ls /dev/serial/by-*

echo
echo
echo "Done."

## (c) 2020 Minh-An Dao. All right reserved