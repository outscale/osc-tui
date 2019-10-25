#!/usr/bin/env python3.6
# encoding: utf-8

from osc_sdk_python import Gateway
import json
import curses
import npyscreen
from virtualMachine import *
import random
from vmLoader import *
from vmInspector import *
import sys
from profileSelector import *
from cockpitForm import CockpitForm

#GLOBALS
RUNNING = True
APP = None
GATEWAY = False
THREADS = list()
#GLOBALS METHODS
def add_thread(t):
    main.THREADS.append(t)
def kill_threads():
    main.RUNNING = False
    for t in THREADS:
        t.stop()
        t.join()
def exit():
    kill_threads()
    sys.exit(0)

class App(npyscreen.StandardApp):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm("MAIN", ProfileSelector, name="osc-cli-curses")

if __name__ == "__main__":
    main.APP = App()
    main.APP.run()

