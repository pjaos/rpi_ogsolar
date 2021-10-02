#!/bin/sh
set -e

#Check the python files and exit on error.
python3.9 -m pyflakes ogsolar/*.py ogsolar/libs/*.py

# Install only for current user
python3.9 -m pip install .

#install for all users
#sudo python3 -m pip install .

#Ensure all files are flush to disk/flash
sync
