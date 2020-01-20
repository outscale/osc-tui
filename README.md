# osc-cli-curses

Designed to be a POC of a Outscale's Cockpit inside the terminal using curses.<br/>The officially supported python version is currently 3.6.<br/> 
Run `./src/main.py` to make it run!<br>
Only the menu `INSTANCES` is currently implemented.<br>

It is currently not compatible with python 3.7 because of the lib npyscreen used.<br/> The code is currently a bit dirty... Maybe big changes are coming!<br>To refresh any table, press [F5].<br>Feel free to suggest oher architectures, libs...<br/>The `src/` folder contains the project's sources.<br/>The `tests/` folder contain some crappy code used to test API calls or any other things...

#Installation
You will need to install:<br>
Python3.6 (https://www.python.org/downloads/release/python-360/)<br>
`pip install npyscreen`<br>
`pip install pyperclip`<br>
OSC-SDK-Python (https://github.com/outscale/osc-sdk-python)<br>
<br>
<br>
You will need to setup the file at `~/.oapi_credentials` as describe in osc-sdk-python's documentation.<br>
