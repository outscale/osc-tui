#!/usr/bin/python3.6
# import json
import json
import os
from pathlib import Path
import threading
import preloader

import npyscreen
import requests
from osc_sdk_python import *

import main
import mainForm
import popup

home = str(Path.home())
dst_file = home + '/.osc/config.json'

OAPI_CREDENTIALS = dict()


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
                            npyscreen.notify_confirm("Error while submitting the request:\n\t- Code = {}\n\t- Reason = {}".format(e.response.status_code, e.response.reason), title="ERROR")
                    if form:
                        kwargs.pop('form')
                        popup.startLoading(form, cb)
                    else:
                        cb()
                    return result

                return wrapped

            # So now we iterate over all methods of the GATEWAY that are not prefixed by "__"
            # and basically we decorate them.
            for method_name in dir(main.GATEWAY):
                if not method_name.startswith("__"):
                    attr = getattr(main.GATEWAY, method_name)
                    if(callable(attr)):
                        wrapped = decorator(attr)
                        setattr(main.GATEWAY, method_name, wrapped)

            # now let's check if the profile worked:
            res = main.GATEWAY.ReadClientGateways(form=self.form)
            if "Errors" not in res:
                preloader.Preloader.load_async()
                mainForm.MODE = 'Vms'
                self.form.parentApp.addForm(
                    "Cockpit", mainForm.MainForm, name="osc-tui")
                self.form.parentApp.switchForm("Cockpit")
            else:
                should_destroy_profile = npyscreen.notify_yes_no(
                    "Credentials are not valids.\nDo you want do delete this profile?", "ERROR", )
                if should_destroy_profile:
                    global OAPI_CREDENTIALS
                    del OAPI_CREDENTIALS[self.name]
                    save_credentials(self.form)
        except requests.ConnectionError:
            npyscreen.notify_confirm(
                "Please check your internet connection.", "ERROR")


class ProfileSelector(npyscreen.ActionFormV2):
    def create(self):
        preloader.Preloader.init()
        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = main.exit
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
            configFile = open(dst_file)
            OAPI_CREDENTIALS = json.loads(configFile.read())
            configFile.close()
            self.add_widget(
                npyscreen.Textfield,
                value="Please select a cockpit profile:",
                editable=False,
            )
            btns = list()
            for c in OAPI_CREDENTIALS:
                bt = self.add_widget(npyscreen.ButtonPress, name="->" + str(c))
                btns.append(bt)
                bt.whenPressed = CallbackFactory(self, str(c))

        def new():
            aksk = popup.readAKSK()
            ok = True
            if aksk:
                for c in aksk:
                    if c in OAPI_CREDENTIALS:
                        ok = False
                        if npyscreen.notify_yes_no(
                                "An existing profile has the same name.\nContinue and overwrite it?", ""):
                            ok = True
                        break
            if ok and aksk:
                OAPI_CREDENTIALS.update(aksk)
                save_credentials(self)

        bt = self.add_widget(npyscreen.ButtonPress, name="NEW PROFILE")
        bt.whenPressed = new
        logo = """

             █████╗  ██████╗ █████╗       ████████╗██╗   ██╗██╗
            ██╔══██╗██╔════╝██╔══██╗      ╚══██╔══╝██║   ██║██║
            ██║  ██║╚█████╗ ██║  ╚═╝█████╗   ██║   ██║   ██║██║
            ██║  ██║ ╚═══██╗██║  ██╗╚════╝   ██║   ██║   ██║██║
            ╚█████╔╝██████╔╝╚█████╔╝         ██║   ╚██████╔╝██║
             ╚════╝ ╚═════╝  ╚════╝          ╚═╝    ╚═════╝ ╚═╝
"""
        self.add_widget(npyscreen.MultiLineEdit, value=logo,
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
