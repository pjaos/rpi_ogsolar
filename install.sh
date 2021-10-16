#!/bin/sh
set -e

rm -rf build ogsolar.egg-info

#Check the python files and exit on error.
python3.9 -m pyflakes ogsolar/*.py ogsolar/libs/*.py

# Install. If this script is executed using sudo then
# ogsolar is installed for all users.
python3.9 -m pip install . --use-feature=in-tree-build

# Upgrade pip to the latest if required
#python3.9 -m pip install --upgrade build
# Build a python whl (wheel) package if required
#python3.9 -m build

#Ensure all files are flush to disk/flash as the raspberry PI
# normally has flash storage.
sync

# Show a list of the installed files
pip show -f ogsolar
