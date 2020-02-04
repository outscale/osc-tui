#!/usr/bin/python3.6
# import json
import json
import os
from pathlib import Path

import npyscreen
import requests
from osc_sdk_python import Gateway

import main
import mainForm
import popup

home = str(Path.home())

OAPI_CREDENTIALS = dict()


def save_credentials(form):
    file = home + "/.oapi_credentials"
    with open(file, "w") as filetowrite:
        filetowrite.write(json.dumps(OAPI_CREDENTIALS))
    form.parentApp.addForm("MAIN", ProfileSelector, name="osc-cli-curses")
    form.parentApp.switchForm("MAIN")


class CallbackFactory:
    def __init__(self, form, name):
        self.form = form
        self.name = name

    def __call__(self):
        try:
            main.GATEWAY = Gateway(**{"profile": self.name})
            res = main.GATEWAY.ReadClientGateways()
            if "Errors" not in res:
                mainForm.MODE = 'INSTANCES'
                self.form.parentApp.addForm(
                    "Cockpit", mainForm.MainForm, name="osc-cli-curses")
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
        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = main.exit
        global OAPI_CREDENTIALS
        OAPI_CREDENTIALS = dict()
        if os.path.isfile(home + "/.oapi_credentials"):
            configFile = open(home + "/.oapi_credentials")
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
