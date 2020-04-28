#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi


echo "This will set up the PS2 Controller's prequisites for Raspberry Pi"


# workaround for automatically calling from main shell script
if ! [ "${1-install}" == "ignore" ] ; then

	apt-get update
	apt-get upgrade -y

fi

# WiringPi  ## http://wiringpi.com/
apt-get install wiringpi -y

# ----------- renew binary files --------------------
chmod +x ps2_bin_reset.sh
./ps2_bin_reset.sh

echo
echo
echo "PS2 Done."

## (c) 2020 Minh-An Dao. All right reserved
