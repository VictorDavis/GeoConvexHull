#!/bin/bash

#Sources:
# https://github.com/VictorDavis/GeoConvexHull
# http://stackoverflow.com/questions/4681737


if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

sudo apt-get --assume-yes install libgeos-dev
sudo pip install shapely
git clone https://github.com/jswhit/pyproj.git
cd pyproj
python setup.py build
sudo python setup.py install
cd ..
rm -rf pyproj

echo "Done."
