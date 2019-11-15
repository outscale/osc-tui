#!/usr/bin/env python3.6
# encoding: utf-8
import sys
import npyscreen
from profileSelector import *

#GLOBALS ATTRIBUTES
RUNNING = True
APP = None
GATEWAY = None
THREADS = list()

#GLOBALS METHODS
def add_thread(t):
    THREADS.append(t)
def kill_threads():
    RUNNING = False
    for t in THREADS:
        t.stop()
        t.join()
def exit():
    kill_threads()
    sys.exit(0)

#APPLICATION CLASS
class App(npyscreen.StandardApp):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm("MAIN", ProfileSelector, name="osc-cli-curses")

#LET'S RUN
if __name__ == "__main__":
    main.APP = App()
    main.APP.run()

