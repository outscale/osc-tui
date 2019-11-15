from cockpitForm import CockpitForm
import json
import npyscreen
from pathlib import Path
from osc_sdk_python import Gateway
import main
home = str(Path.home())


class CallbackFactory():
    def __init__(self, form, name):
        self.form = form
        self.name = name

    def __call__(self):
        main.GATEWAY = Gateway(**{'profile': self.name})
        self.form.parentApp.addForm(
            "Cockpit", CockpitForm, name="osc-cli-curses")
        self.form.parentApp.switchForm('Cockpit')


class ProfileSelector(npyscreen.ActionFormV2):
    def create(self):
        configFile = open(home + '/.oapi_credentials')
        config = json.loads(configFile.read())
        configFile.close()
        btns = list()
        for c in config:
            bt = self.add_widget(npyscreen.ButtonPress, name=str(c))
            btns.append(bt)
        for bt in btns:
            bt.whenPressed = CallbackFactory(self, bt.name)

    def create_control_buttons(self):
        self._add_button('cancel_button',
                         self.__class__.CANCELBUTTON_TYPE,
                         'Exit',
                         0 - self.__class__.CANCEL_BUTTON_BR_OFFSET[0],
                         0 -
                         self.__class__.CANCEL_BUTTON_BR_OFFSET[1] - len(
                             self.__class__.CANCEL_BUTTON_TEXT),
                         None
                         )

    def on_cancel(self):
        main.exit()
