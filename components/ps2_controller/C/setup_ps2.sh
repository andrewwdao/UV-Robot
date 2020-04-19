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
# load the SPI drivers into the kernel # https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md
									   # http://wiringpi.com/reference/spi-library/
# check if the phrase "dtparam=spi=on" has been uncommented in the file or not
if [ 0 -eq $( grep -c '#dtparam=spi=on' /boot/config.txt ) ]; then
	sed -i '/dtparam=spi=on/s/^#//g' /boot/config.txt
fi


echo "Please reboot to make SPI enable."

## (c) 2020 Minh-An Dao. All right reserved