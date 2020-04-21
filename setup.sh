#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi

echo -n "Confirm to install? [Y/N]"

read input

if ! [ $input == "y" ] || [ $input == "Y" ]; then
	{ echo "Exiting..."; exit 1; }
fi

echo "Installing..."

# automatically get and set time from the internet (workaround for proxy setting)
date -s "$(wget -qSO- --max-redirect=0 google.vn 2>&1 | grep Date: | cut -d' ' -f5-8)Z"

apt-get update
apt-get upgrade -y
# update all the kept-back if existed  # # https://askubuntu.com/questions/601/the-following-packages-have-been-kept-back-why-and-how-do-i-solve-it
apt-get --with-new-pkgs upgrade -y

# pip installation
apt-get install python3-pip -y

# git installation
apt-get install wget git -y


cd /home/$(who am i | awk '{print $1}')/ # return to home folder -- cannot use $USER or $LOGNAME since they may return root. $SUDO_USER can also be used but not all covered. ref: https://stackoverflow.com/questions/4598001/how-do-you-find-the-original-user-through-multiple-sudo-and-su-commands

# ---------------- download system files from git repository
if [ -d "./system" ] ; then  # check if the directory exist or not
	rm -rf ./system
fi
mkdir ./system
cd ./system
git init
git clone https://github.com/minhan74/UV-Robot.git

# ---------------- setup all the prequisites
cd /home/$(who am i | awk '{print $1}')/system/main
# setup streaming server
chmod +x setup_server.sh
./setup_server.sh ignore
# setup database
chmod +x setup_db.sh
./setup_db.sh ignore
# setup motor
chmod +x setup_motor.sh
./setup_motor.sh ignore
# setup ps2
chmod +x setup_ps2.sh
./setup_ps2.sh ignore

# provide priveledge for setup itself
chmod +x ../setup.sh

echo
echo
echo "Done."
echo
echo "(c) 2020 Minh-An Dao <bit.ly/DMA-HomePage> <minhan7497@gmail.com>. All right reserved ."

## (c) 2020 Minh-An Dao. All right reserved