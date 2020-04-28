#!/bin/bash

set -eu -o pipefail # fail on error , debug all lines

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root! ( sudo ${0} )"
  exit 1;
fi

echo "This will reset PS2 Controller's binary for Raspberry Pi"

# ----------- renew binary files --------------------
# go to cpp code section, clean the c binary files and re-create them
cd ./ps2x
make clean   # cd /home/$(who am i | awk '{print $1}')/system/main/ps2x
rm -rf ./obj
mkdir ./obj
make
mkdir /ps2x
cp ./ps2x /ps2x/ps2x

echo
echo
echo "Binary reset."

## (c) 2020 Minh-An Dao. All right reserved