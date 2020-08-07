# osc-tui

Designed to be a POC of a Outscale's Cockpit inside the terminal using curses.<br/>The officially supported python version is currently 3.<br/> The code is currently a bit dirty... Maybe big changes are coming!<br>To refresh any table, press [F5].<br>Feel free to suggest oher architectures, libs...<br/>The `src/` folder contains the project's sources.<br/>The ```tests/``` folder contain some crappy code used to test API calls or any other things...

# Installation

You will need to install python3:<br>

* Python3 (https://www.python.org/downloads/).

## The easy way:

* `bash <(curl -s https://raw.githubusercontent.com/outscale-dev/osc-tui/master/setup.sh)`

## The tricky one:

Now you can clone the repository:
<br>

* `git clone https://github.com/outscale-dev/osc-tui.git`

<br>

And then open the project's folder: <br>

* `cd osc-tui`
* `git submodule update --init`

<br>

Then setup a virtual environnement (Facultative but recommended):<br>
* Install `virtualenv`: `python3 -m pip install virtualenv`
* Create the environnement: `python3 -m virtualenv -p python3 env`
* Activate it: `source env/bin/activate`.
* To exit use `deactivate`.

<br>
You will need to install:<br>

* `python3 -m pip install pyperclip`.
* `python3 -m pip install autopep8`.
* `python3 -m pip install requests`.
* OSC-SDK-Python (https://github.com/outscale/osc-sdk-python), `python3 -m pip install https://github.com/outscale/osc-sdk-python/releases/download/0.9.15/osc_sdk_python-0.9.15-py3-none-any.whl`.

And now npyscreen:
* `cd npyscreen`
* `python3 setup.py build`
* `python3 setup.py install`
* `cd ..`

<br>

Now configure the project:
* `./configure --dev`: allow running directly `main.py` file.
* `./configure --release`: before packaging the app.


Finally run it! (must be configured in `--dev`)<br>

* `./src/main.py`

# Contributing

Just a few rules:<br>
* Format correctly your code (you can do `autopep8 --in-place --aggressive --aggressive src/*.py`).
* Add external dependencies as less as possible.


