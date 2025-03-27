
#!/usr/bin/env python3
# encoding: utf-8
import sys
import os
import json

import osc_npyscreen
from requests import get

from osc_sdk_python import authentication

from typing import List

from osc_tui import profileSelector
from osc_tui import guiRules

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
try:
    IP = get("https://api.ipify.org").text
except (Exception,KeyboardInterrupt):
    IP="UNKNOW"
# Because it's cool but also a DDOS attack :)
# So let's be cool with the API --> No auto refresh!
POLL_ENABLED = False
VERSION = 250300
# GLOBALS METHODS

CURRENT_GRID=None
SEARCH_FILTER=""

def readVms():
    reply = GATEWAY.ReadVms()
    if reply is None:
        return None
    return reply["Vms"]


def add_thread(t):
    THREADS.append(t)


def kill_threads():
    for t in THREADS:
        t.stop()
        t.join()


def exit():
    kill_threads()
    sys.exit(0)


def do_search(array, lookup_list: List[str], name_as_tag=False, az=False, state_msg=False, accepted_net=False):
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


class App(osc_npyscreen.NPSAppManaged):
    def txtColotToTheme(self, color):
        if color == "Default":
            return osc_npyscreen.Themes.DefaultTheme
        elif color == "Elegant":
            return osc_npyscreen.Themes.ElegantTheme
        elif color == "Colorful":
            return osc_npyscreen.Themes.ColorfulTheme
        elif color == "BlackOnWhite":
            return osc_npyscreen.Themes.BlackOnWhiteTheme
        elif color == "TransparentDark":
            return osc_npyscreen.Themes.TransparentThemeDarkText
        elif color == "TransparentLight":
            return osc_npyscreen.Themes.TransparentThemeLightText
        return osc_npyscreen.Themes.DefaultTheme

    def __init__(self, color):
        self.colorTheme = self.txtColotToTheme(color)
        super().__init__()

    def onStart(self):
        osc_npyscreen.setTheme(self.colorTheme)
        self.addForm("MAIN", profileSelector.ProfileSelector,
                     name="osc-tui")

def help():
    print(
"""usage: osc-tui [OPTION]

-v, --version:          print version
-h, --help:             print this help
    --profile [PROFILE] select default profile, list all profiles if PROFILE not found
    --color-theme [THEME]         select default color theme
    --mode MODE         select default mode
    --ascii-logo        use ascii for logo
"""
    )

def main():
    color=None
    argc = len(sys.argv)
    argv = sys.argv

    if argc > 1:
        i = 1
        while i < argc:
            a = argv[i]
            if a == "--version" or a == "-v":
                print("osc-tui: ", VERSION, " osc-sdk-python: ", authentication.VERSION)
                return 0
            elif a == "--help" or a =="-h":
                help()
                return 0
            elif a == "--mode":
                i += 1
                if i == argc:
                    print(
"""
--mode require an argument !!!, mode list:
Vms Security Volumes Snapshots Keypairs Images LoadBalancers Nets Subnets
PublicIps Nics NetAccessPoints NetPeering InternetServices NatServices
RouteTables DhcpOptions GPUs
""")
                    return 1
                profileSelector.MODE = argv[i]
            elif a == "--color-theme":
                i += 1
                if i == argc:
                    print("--color-theme require one of those theme: Default, Elegant, Colorful, BlackOnWhite, TransparentDark, TransparentLight")
                    return 0;
                color=argv[i]
            elif a == "--profile":
                i += 1
                if i == argc:
                    if os.path.isfile(profileSelector.dst_file):
                        with open(profileSelector.dst_file, 'r') as configFile:
                            OAPI_CREDENTIALS = json.loads(configFile.read())
                            print("Profiles:")
                            for c in OAPI_CREDENTIALS:
                                print(str(c))
                    else:
                        print("{} not found, can't read profile !!!".
                              format(profileSelector.dst_file),
                              file=sys.stderr)
                    return 0
                profileSelector.PROFILE = argv[i]
            elif a == "--ascii-logo":
                profileSelector.ASCII_LOGO = True
            else:
                print("unknow argument: ", a)
                help()
                return 1
            i += 1

    try:
        guiRules.parse()
        APP = App(color)
        APP.run()
    except KeyboardInterrupt:
        kill_threads()
        print("Program quit by Ctrl-C")
        sys.exit(130)
    return 0

# LET'S RUN
if __name__ == "__main__":
    sys.exit(main())
