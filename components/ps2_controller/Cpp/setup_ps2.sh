#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi

echo "This will set up the PS2 Controller's prequisites for Raspberry Pi"

# workaround for automatically calling from main shell script
if ! [ "$1" == "ignore" ] ; then

	apt-get update
	apt-get upgrade -y

fi

# WiringPi  ## http://wiringpi.com/
apt-get install wiringpi -y

# ----------- renew binary files --------------------
# go to cpp code section, clean the c binary files and re-create them
cd ./ps2x
make clean   # cd /home/$(who am i | awk '{print $1}')/system/main/ps2x
rm -rf ./obj
mkdir ./obj
make

echo
echo
echo "PS2 Done."

## (c) 2020 Minh-An Dao. All right reserved