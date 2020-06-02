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
git clone https://github.com/minhan74/UV-Robot.git
# change name
mv UV-Robot/ system/


# ---------------- setup all the prequisites
cd /home/$(who am i | awk '{print $1}')/system/main
# provide priveledge for setup itself
chmod +x ../setup.sh

# setup control server
chmod +x server_setup.sh
./server_setup.sh ignore
# setup motor
chmod +x motor_setup.sh
./motor_setup.sh ignore
# setup ps2
chmod +x ps2_setup.sh
./ps2_setup.sh ignore
# setup relay
chmod +x relay_setup.sh
./relay_setup.sh ignore

# disable bluetooth
chmod +x bluetooth_disable.sh
./bluetooth_disable.sh

# make system read-only
chmod +x ./readonly/setup.sh
./readonly/setup.sh yes


# --------------- activate system on start-up
# UVrobot.service
echo "[Unit]
Description=MIS-CTU UV disinfection robot service
After=multi-user.target
DefaultDependencies=true


[Service]
Type=simple
# This will release the same result: ExecStart = /usr/bin/sudo python3 -u main.py
ExecStart=sudo python3 -u main.py
WorkingDirectory=/home/$(who am i | awk '{print $1}')/system/main
StandardOutput=inherit
StandardError=inherit
Restart=yes
# must set user to root to execute all functions and peripherals
User=root
# SIGINT is translated as a KeyboardInterrupt exception by Python.
# default kill signal is SIGTERM which doesn't raise an exception in Python.
# KillSignal=SIGINT
# Additional commands that are executed after the service is stopped. ref: https://www.freedesktop.org/software/systemd/man/systemd.service.html
# ExecStopPost=sudo python3 -u syshalt.py

 
[Install]
WantedBy=sysinit.target multi-user.target
" > /etc/systemd/system/UVrobot.service # append multiple lines to a file : https://unix.stackexchange.com/questions/77277/how-to-append-multiple-lines-to-a-file
systemctl enable UVrobot.service


echo
echo
echo "Done. Please reboot."
echo
echo "(c) 2020 Minh-An Dao <bit.ly/DMA-HomePage> <minhan7497@gmail.com>. All right reserved ."

## (c) 2020 Minh-An Dao. All right reserved