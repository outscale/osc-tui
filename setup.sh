#!/bin/bash
set -e 
git clone https://github.com/outscale-dev/osc-tui.git
cd osc-tui
git submodule update --init
python3 -m pip install virtualenv
python3 -m virtualenv -p python3 env
source env/bin/activate
python3 -m pip install pyperclip
python3 -m pip install autopep8
python3 -m pip install nuitka
python3 -m pip install https://github.com/outscale/osc-sdk-python/releases/download/0.10.0/osc_sdk_python-0.10.0-py2.py3-none-any.whl
cd oscscreen
python3 setup.py build
python3 setup.py install
cd ..
./configure.sh --dev
read -p "Do you want to build and install osc-tui (y/n) ?" -n 1 -r
echo    # (optional) move to a new line
if [ "$REPLY" == "y" ] || [ "$1" == "-y" ] && [ "$1" != "-n" ]; then
    make osc-tui
    make install
fi
deactivate
