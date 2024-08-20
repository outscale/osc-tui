#!/usr/bin/python3.6
# import json
import json
import os
from pathlib import Path
from osc_tui import preloader

import osc_npyscreen
import requests
from osc_sdk_python import *

from osc_tui import main
from osc_tui import mainForm
from osc_tui import popup

import traceback

home = str(Path.home())
dst_file = home + '/.osc/config.json'

OAPI_CREDENTIALS = dict()
ASCII_LOGO = False

MODE="Vms"

PROFILE=None

RULES=None

def save_credentials(form):
    file = dst_file
    if not os.path.exists(os.path.dirname(dst_file)):
        os.makedirs(os.path.dirname(dst_file), mode=0o700)
    with open(file, "w") as filetowrite:
        filetowrite.write(json.dumps(OAPI_CREDENTIALS))
    form.parentApp.addForm("MAIN", ProfileSelector, name="osc-tui")
    form.parentApp.switchForm("MAIN")


class CallbackFactory:
    def __init__(self, form, name):
        self.form = form
        self.name = name

    def __call__(self):
        try:
            global res
            main.GATEWAY = Gateway(**{"profile": self.name, "user_agent": "osc-tui/" + str(main.VERSION) + " " + authentication.DEFAULT_USER_AGENT})

            if hasattr(main.GATEWAY.log, "config"):
                main.GATEWAY.log.config(type=LOG_MEMORY, what=LOG_KEEP_ONLY_LAST_REQ)

            # The following code is a little bit completely tricky :)
            # Here is the idea:
            # I want to hook all calls to the main.GATEWAY modules to automatically display the pending animation.
            # (So it's a decorator)
            # However, for doing such things I need to add a form parameter.
            # However 2, when performing one call, it will do some "inner calls" so we must not trigger the animation all the time.
            # One way would be to decorate only the "main functions" but I wanna do it automatically!
            # Another one is the following one:
            # If we have the form parameter, we remove it form kwargs and start the pending animation.
            # So the pending animation won't be started again during "inner
            # calls".

            def decorator(func):
                def wrapped(*args, **kwargs):
                    form = kwargs.get('form')
                    global result
                    result = None
                    def cb():
                        global result
                        try:
                            result = func(*args, **kwargs)
                        except requests.exceptions.HTTPError as e:
                            popup.pauseLoader()
                            osc_npyscreen.notify_confirm(
                                "Error while submitting the request:\n{}\nCode: {}\nReason: {}".
                                format(main.GATEWAY.log.str(),
                                       e.response.status_code,
                                       e.response.reason),
                                title="ERROR", wide=True)
                    if form:
                        kwargs.pop('form')
                        popup.startLoading(form, cb)
                    else:
                        cb()
                    return result

                return wrapped

            def get_action_wrapper(*args, **kwargs):
                action_name = args[0]
                wrapped = decorator(self.gtw_get_action(action_name))
                return wrapped

            # So now we iterate over all methods of the GATEWAY that are not prefixed by "__"
            # and basically we decorate them.
            for method_name in dir(main.GATEWAY):
                if method_name == "_action":
                    attr = getattr(main.GATEWAY, method_name)
                    wrapped = decorator(attr)
                    setattr(main.GATEWAY, method_name, wrapped)
                elif method_name == "_get_action":
                    self.gtw_get_action = main.GATEWAY._get_action
                    setattr(main.GATEWAY, '_get_action', get_action_wrapper)

            # now let's check if the profile worked:
            try:
                res = main.GATEWAY.ReadClientGateways(form=self.form)
                if res is not None and "Errors" not in res:
                    preloader.Preloader.load_async()
                    mainForm.MODE = MODE
                    self.form.parentApp.addForm(
                        "Cockpit", mainForm.MainForm, name="osc-tui")
                    self.form.parentApp.switchForm("Cockpit")
                else:
                    should_destroy_profile = osc_npyscreen.notify_yes_no(
                        "Credentials are not valids.\nDo you want do delete this profile?", "ERROR", )
                    if should_destroy_profile:
                        global OAPI_CREDENTIALS
                        del OAPI_CREDENTIALS[self.name]
                        save_credentials(self.form)
            except Exception as e:
                osc_npyscreen.notify_confirm("Exeption trow: \"{}\"\nLog in ./osc-tui.log".format(str(e)))
                traceback.print_exc(file=open("osc-tui.log", "w"))
                main.kill_threads()
                exit(1)
        except requests.ConnectionError:
            osc_npyscreen.notify_confirm(
                "Please check your internet connection.", "ERROR")


class ProfileSelector(osc_npyscreen.ActionFormV2):
    to_call=None
    def create(self):
        preloader.Preloader.init()
        self.how_exited_handers[osc_npyscreen.wgwidget.EXITED_ESCAPE] = main.exit
        global OAPI_CREDENTIALS
        global dst_file
        OAPI_CREDENTIALS = dict()
        have_file = False
        if os.path.isfile(dst_file):
            have_file = True
        elif os.path.isfile(home + "/.oapi_credentials"):
            dst_file = home + "/.oapi_credentials"
            have_file = True

        if have_file:
            try:
                configFile = open(dst_file)
                OAPI_CREDENTIALS = json.loads(configFile.read())
                configFile.close()
            except json.decoder.JSONDecodeError:
                osc_npyscreen.notify_confirm("Fail to decode '{}', json most-likely broken".format(dst_file))
                exit(1)
            self.add_widget(
                osc_npyscreen.Textfield,
                value="Please select a cockpit profile:",
                editable=False,
            )
            btns = list()
            for c in OAPI_CREDENTIALS:
                bt = self.add_widget(osc_npyscreen.ButtonPress, name="->" + str(c))
                btns.append(bt)
                bt.whenPressed = CallbackFactory(self, str(c))
                if str(c) == PROFILE:
                    self.to_call=bt

        def new():
            aksk = popup.readAKSK()
            ok = True
            if aksk:
                for c in aksk:
                    if c in OAPI_CREDENTIALS:
                        ok = False
                        if osc_npyscreen.notify_yes_no(
                                "An existing profile has the same name.\nContinue and overwrite it?", ""):
                            ok = True
                        break
            if ok and aksk:
                OAPI_CREDENTIALS.update(aksk)
                save_credentials(self)

        bt = self.add_widget(osc_npyscreen.ButtonPress, name="NEW PROFILE")
        bt.whenPressed = new
        logo_complex = """

             █████╗  ██████╗ █████╗       ████████╗██╗   ██╗██╗
            ██╔══██╗██╔════╝██╔══██╗      ╚══██╔══╝██║   ██║██║
            ██║  ██║╚█████╗ ██║  ╚═╝█████╗   ██║   ██║   ██║██║
            ██║  ██║ ╚═══██╗██║  ██╗╚════╝   ██║   ██║   ██║██║
            ╚█████╔╝██████╔╝╚█████╔╝         ██║   ╚██████╔╝██║
             ╚════╝ ╚═════╝  ╚════╝          ╚═╝    ╚═════╝ ╚═╝
"""
        logo_simple = """
           ___  ____   ____         _____ _   _ ___ 
          / _ \/ ___| / ___|       |_   _| | | |_ _|
         | | | \___ \| |     _____   | | | | | || | 
         | |_| |___) | |___ |_____|  | | | |_| || | 
          \___/|____/ \____|         |_|  \___/|___|
"""

        logo = logo_complex if not ASCII_LOGO else logo_simple
        self.add_widget(osc_npyscreen.MultiLineEdit, value=logo,
                        editable=False, multiline=True)

    def create_control_buttons(self):
        self._add_button(
            "cancel_button",
            self.__class__.CANCELBUTTON_TYPE,
            "Exit",
            0 - self.__class__.CANCEL_BUTTON_BR_OFFSET[0],
            0
            - self.__class__.CANCEL_BUTTON_BR_OFFSET[1]
            - len(self.__class__.CANCEL_BUTTON_TEXT),
            None,
        )

    def on_cancel(self):
        main.exit()

    def quit():
        main.kill_threads()
        exit()
        
    def set_up_handlers(self):
        super().set_up_handlers()
        self.add_handlers({"^Q": quit})
        self.add_handlers({"q": quit})


    def on_screen(self):
        if self.to_call != None:
            self.to_call.whenPressed()
            self.to_call=None
        else:
            super().on_screen()
