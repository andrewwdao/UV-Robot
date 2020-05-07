#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi


echo "This will reset ultrasonic sensor's binary for Raspberry Pi"


# ----------- renew binary files --------------------
# go to cpp code section, clean the c binary files and re-create them
cd ./ultrasonic
make clean   # cd /home/$(who am i | awk '{print $1}')/system/main/ps2x
rm -rf ./obj
mkdir ./obj
make
if [ -d "/ultrasonic" ] ; then  # check if the directory exist or not
	rm -rf /ultrasonic
fi
mkdir /ultrasonic
cp ./ultrasonic /ultrasonic/ultrasonic

echo
echo
echo "Binary reset."

## (c) 2020 Minh-An Dao. All right reserved
