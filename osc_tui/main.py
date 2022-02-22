#!/usr/bin/env python3
# encoding: utf-8
import sys

import npyscreen
from requests import get

from osc_sdk_python import authentication

import inputForm
import profileSelector

import time

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
VERSION = 211130
# GLOBALS METHODS

CURRENT_GRID=None
SEARCH_FILTER=""

def add_thread(t):
    THREADS.append(t)


def kill_threads():
    for t in THREADS:
        t.stop()
        t.join()


def exit():
    kill_threads()
    sys.exit(0)


def do_search(array, lookup_list, name_as_tag=False, az=False, state_msg=False, accepted_net=False):
    if len(SEARCH_FILTER) < 1:
        return array
    to_remove = []

    for val in array:
        is_okay = False

        if state_msg and 'State' in val and val['State']['Message'].find(SEARCH_FILTER) != -1:
            is_okay = True

        if accepted_net and "AccepterNet" in val and val["AccepterNet"]["NetId"].find(SEARCH_FILTER) != -1:
            is_okay = True

        if name_as_tag and len(val["Tags"]) > 0 and val["Tags"][0]["Value"].find(SEARCH_FILTER) != -1:
            is_okay = True

        if az and "Placement" in val and val["Placement"]["SubregionName"].find(SEARCH_FILTER) != -1:
            is_okay = True

        if is_okay == False:
            for s in lookup_list:
                if (s in val) and str(val[s]).find(SEARCH_FILTER) != -1:
                    is_okay = True
                    break
        if is_okay == False:
            to_remove.append(val)

    for to_rm in to_remove:
        array.remove(to_rm)
    return array

# APPLICATION CLASS


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(npyscreen.Themes.DefaultTheme)
        self.addForm("MAIN", profileSelector.ProfileSelector,
                     name="osc-tui")

def help():
    print(
"""
usage: osc-tui [OPTION]

-v, --version:          print version
-h, --help:             print this help
    --ascii-logo        use ascii for logo
"""
    )

def main():
    argc = len(sys.argv)
    argv = sys.argv

    if argc > 1:
        for i in range(1, argc):
            a = argv[i]
            if a == "--version" or a == "-v":
                print("osc-tui: ", VERSION, " osc-sdk-python: ", authentication.VERSION)
                return 0
            elif a == "--help" or a =="-h":
                help()
                return 0
            elif a == "--ascii-logo":
                profileSelector.ASCII_LOGO = True
            else:
                print("unknow argument: ", a)
                help()
                return 1

    try:
        APP = App()
        APP.run()
    except KeyboardInterrupt:
        kill_threads()
        print("Program quit by Ctrl-C")
        sys.exit(130)
    return 0

# LET'S RUN
if __name__ == "__main__":
    sys.exit(main())
