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
    form.parentApp.addForm("MAIN", ProfileSelector, name="osc-tui")
    form.parentApp.switchForm("MAIN")


class CallbackFactory:
    def __init__(self, form, name):
        self.form = form
        self.name = name

    def __call__(self):
        try:
            global res
            main.GATEWAY = Gateway(**{"profile": self.name})

            def load_information():
                main.SUBREGION_LIST = main.GATEWAY.ReadSubregions(form=self)["Subregions"]
                main.IMAGEVM_LIST = main.GATEWAY.ReadImages(form=self)["Images"]
                main.VMTYPE_LIST = main.GATEWAY.ReadVmTypes(form=self)["VmTypes"]

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
                    if form:
                        kwargs.pop('form')

                        def cb():
                            global result
                            result = func(*args, **kwargs)
                        popup.startLoading(form, cb)
                    else:
                        result = func(*args, **kwargs)
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
                load_information()
                mainForm.MODE = 'INSTANCES'
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
