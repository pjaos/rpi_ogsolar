#!/bin/sh

HOST=192.168.0.164

#The folder to scp the installer files into.
TARGET_FOLDER=/home/pi/pip/rpi_ogsolar

scp -r ogsolar/* pi@$HOST:$TARGET_FOLDER/ogsolar
scp -r scripts/* pi@$HOST:$TARGET_FOLDER/scripts
scp install.sh uninstall.sh setup.py README.md pi@$HOST:$TARGET_FOLDER






