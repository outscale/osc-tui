# osc-cli-curses

Designed to be a POC of a Outscale's Cockpit inside the terminal using curses.<br/>The officially supported python version is currently 3.6.<br/>
But with this fork of npyscreen: https://github.com/jwoglom/npyscreen you can run it in python 3.7.<br>
Only the menu `INSTANCES` is currently implemented.<br>

It is currently not compatible with python 3.7 because of the lib npyscreen used.<br/> The code is currently a bit dirty... Maybe big changes are coming!<br>To refresh any table, press [F5].<br>Feel free to suggest oher architectures, libs...<br/>The `src/` folder contains the project's sources.<br/>The ```tests/``` folder contain some crappy code used to test API calls or any other things...

# Installation

You will need to install:<br>
* Python3.6 (https://www.python.org/downloads/release/python-360/)<br>
* `pip install npyscreen`<br>
* `pip install pyperclip`<br>
* OSC-SDK-Python (https://github.com/outscale/osc-sdk-python)<br>
<br>
<br>
Now you can clone the repository:
<br>

`git clone https://github.com/outscale/osc-sdk-python.git`<br>

And then open the project's folder: <br>

`cd osc-cli-curses`<br>

Finally run it!<br>

`./src/main.py`
