#!/usr/bin/env python3
# encoding: utf-8
import sys

import npyscreen
from requests import get

import inputForm
import profileSelector

# GLOBALS ATTRIBUTES
APP = None
GATEWAY = None
THREADS = list()
VM = None
VMs = None
LBU = None
LBUs = None
VPCs = None
SECURITY_GROUP = None
SECURITY_RULE = None
IP = get("https://api.ipify.org").text
# Because it's cool but also a DDOS attack :)
# So let's be cool with the API --> No auto refresh!
POLL_ENABLED = False
VERSION = 210500
# GLOBALS METHODS


def add_thread(t):
    THREADS.append(t)


def kill_threads():
    for t in THREADS:
        t.stop()
        t.join()


def exit():
    kill_threads()
    sys.exit(0)


# APPLICATION CLASS


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.ColorfulTheme)
        self.addForm("MAIN", profileSelector.ProfileSelector,
                     name="osc-tui")


# LET'S RUN
if __name__ == "__main__":
    APP = App()
    APP.run()


def main():
    APP = App()
    APP.run()
