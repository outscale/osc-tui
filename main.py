from osc_sdk_python import Gateway
import json
#!/usr/bin/env python
# encoding: utf-8
import curses
import npyscreen
from virtualMachine import *
import random
from vmLoader import *
from vmInspector import *
import sys
from profileSelector import *
from cockpitForm import CockpitForm

RUNNING = True
APP = None
GATEWAY = False

class App(npyscreen.StandardApp):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm("MAIN", ProfileSelector, name="osc-cli-curses")


THREADS = list()
def add_thread(t):
    THREADS.append(t)

def exit():
    RUNNING = False
    for t in THREADS:
        t.stop()
        t.join()
    sys.exit(0)

#print(gw.ReadVms())
if __name__ == "__main__":
    APP = App()
    APP.run()
    #print(summary_titles())
    print('Correctly exited...')

