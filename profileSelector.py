import json
import npyscreen
from pathlib import Path
from osc_sdk_python import Gateway
import main
home = str(Path.home())
from cockpitForm import CockpitForm
class ProfileSelector(npyscreen.ActionPopup):
    def create(self):
        configFile = open(home + '/.oapi_credentials')
        config = json.loads(configFile.read())
        configFile.close()
        choices = list()
        for c in config:
            choices.append(str(c))
        self.picker = self.add(npyscreen.TitleSelectOne, center = True, max_height=4, value = [0,], name="Select a cockpit profile:",
        values = choices, scroll_exit=True)
    def on_ok(self):
        profile = self.picker.get_selected_objects()[0]
        main.GATEWAY = Gateway(**{'profile': profile})
        self.parentApp.addForm("Cockpit", CockpitForm, name="osc-cli-curses")
        self.parentApp.switchForm('Cockpit')

    def on_cancel(self):
        main.exit()