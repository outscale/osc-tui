# osc-tui

Designed to be a POC of a Outscale's Cockpit inside the terminal using curses.<br/>The officially supported python version is currently 3.<br/> The code is currently a bit dirty... Maybe big changes are coming!<br>To refresh any table, press [F5].<br>Feel free to suggest oher architectures, libs...<br/>The `src/` folder contains the project's sources.<br/>The ```tests/``` folder contain some crappy code used to test API calls or any other things...

# Installation

You will need to install python3:<br>

* Python3 (https://www.python.org/downloads/).

Now you can clone the repository:
<br>

* `git clone https://github.com/outscale-dev/osc-tui.git`

<br>

And then open the project's folder: <br>

* `cd osc-tui`
* `git submodule init`
* `git submodule update`

<br>

Then setup a virtual environnement (Facultative but recommended):<br>
* Install `virtualenv`: `python3 -m pip install virtualenv`
* Create the environnement: `python3 -m virtualenv -p python3 env`
* Activate it: `source env/bin/activate`.
* To exite use `deactivate`.

<br>
You will need to install:<br>

* `python3 -m pip install pyperclip`.
* `python3 -m pip install autopep8`.
* OSC-SDK-Python (https://github.com/outscale/osc-sdk-python).

And now npyscreen:
* `cd npyscreen`
* `python3 setup.py build`
* `python3 setup.py install`
* `cd ..`

<br>


Finally run it!<br>

* `./src/main.py`

# Contributing

Just a few rules:<br>
* Format correctly your code (you can do `autopep8 --in-place --aggressive --aggressive src/*.py`).
* Format correctly your commits(`myFolfder: what I Did`, or `myFolder/test.py: what I did`).
* Add external dependencies as less as possible.

<br>Note that the commit standard is new now so not really applied yet.
