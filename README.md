# osc-cli-curses

Designed to be a POC of a Outscale's Cockpit inside the terminal using curses.<br/>The officially supported python version is currently 3.6.<br/>
But with this fork of npyscreen: https://github.com/jwoglom/npyscreen you can run it in python 3.7 and 3.8.<br>
Only the menu `INSTANCES` is currently implemented.<br>

It is currently not compatible with python 3.7 because of the lib npyscreen used.<br/> The code is currently a bit dirty... Maybe big changes are coming!<br>To refresh any table, press [F5].<br>Feel free to suggest oher architectures, libs...<br/>The `src/` folder contains the project's sources.<br/>The ```tests/``` folder contain some crappy code used to test API calls or any other things...

# Installation

You will need to install python3.6:<br>

* Python3.6 (https://www.python.org/downloads/release/python-360/).

Now you can clone the repository:
<br>

* `git clone https://github.com/outscale/osc-sdk-python.git`<br>

<br>

And then open the project's folder: <br>

* `cd osc-cli-curses`

<br>

Then setup a virtual environnement (Facultative but recommended):<br>
* Install `virtualenv`: `python3.6 -m pip install virtualenv`
* Create the environnement: `python3.6 -m virtualenv -p python3.6 env`
* Activate it: `source env/bin/activate`.
* To exite use `deactivate`.

<br>
You will need to install:<br>

* `python3.6 -m pip install npyscreen`.
* `python3.6 -m pip install pyperclip`.
* `python3.6 -m pip install autopep8`.
* OSC-SDK-Python (https://github.com/outscale/osc-sdk-python).

<br>


Finally run it!<br>

* `./src/main.py`

# Contributing

Just a few rules:<br>
* Format correctly your code (you can do `autopep8 --in-place --aggressive --aggressive src/*.py`).
* Format correctly your commits(`myFolfder: what I Did`, or `myFolder/test.py: what I did`).
* Add external dependencies as less as possible.

<br>Note that the commit standard is new now so not really applied yet.
