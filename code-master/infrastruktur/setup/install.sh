#!/bin/bash

echo "Notwendige Programme installieren..."
sudo apt-get update
sudo apt-get install python-virtualenv python-dev libevent-dev cmake  python-opencv\
        libboost-serialization-dev libboost-system-dev libboost-dev libboost-thread-dev\
        libboost-iostreams-dev python-argparse python-setuptools python-gtk2\
        python-gevent python-glade2 llvm clang libgtest-dev python-gobject libyaml-cpp-dev

sudo apt-get install libcv-dev
sudo apt-get install libopencv-dev
#sudo apt-get install libopencv-gpu-dev libopencv-contrib-dev
sudo apt-get install libeigen3-dev

sudo apt-get install graphviz

#In den Ordner des Skriptes wechseln
cd $(readlink -f $(dirname $0))
echo "Environment erzeugen"
ROOT=`git rev-parse --show-toplevel`/.py-env
if [[ $ROOT =~ ^/homes/[0-9][0-9] ]] ; then # We are on our LDUP system
    mkdir /local/${HOME/\/homes\//}
    DEFAULT_ROOT=$ROOT
    ROOT=/local/${HOME/\/homes\//}/py-env
    ln -s $ROOT $DEFAULT_ROOT
fi
if virtualenv | grep -q system-site-package ; then
    virtualenv $ROOT --system-site-packages
else
    virtualenv $ROOT
fi

echo "Environment aktivieren"
. $ROOT/bin/activate

echo "Abhängigkeiten installieren"

pip install gevent-socketio cython construct sphinx urwid mock xdot matplotlib pyyaml

echo "Finished installation successfully."
echo -e "Type: \nsource ${ROOT}/bin/activate\nto activate the virtualenv for building the software "
