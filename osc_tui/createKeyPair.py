import oscscreen
from osc_tui import main
from osc_tui import popup
import os

from os.path import expanduser

# This file is here for creating a keypair and downloading the generated private key.
# Currently, it downloads it on ~/Downloads.
# Later, we will be able to create a key from an existing private key, and to install created keys in
# a cleaner way.

# NAME input.
NAME = None


class CreateKeyPair(oscscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm(
            "CREATE_KEYPAIR",
            CreateSnapshot,
            name="osc-tui")
        self.parentApp.switchForm("CREATE_KEYPAIR")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def write_key(path, private_key):
            key_file = open(os.path.expanduser(path), 'w')
            key_file.write(private_key)
            key_file.close()

        def create():
            if(NAME.get_value()):
                res = main.GATEWAY.CreateKeypair(
                    form=self,
                    KeypairName=NAME.get_value())
                if 'Errors' not in res and 'Keypair' in res:
                    private_key = res['Keypair']['PrivateKey']
                    name = res['Keypair']['KeypairName']
                    home = expanduser('~')
                    if os.path.isdir(home+"/Downloads"):
                        path = '~/Downloads/' + name + ".rsa"
                        write_key(path, private_key) 
                    else:
                        if not os.path.isdir(home+"/.osc/keypair"):
                            os.makedirs(home + "/.osc/keypair")
                        path = "~/.osc/keypair/" + name + ".rsa"
                        write_key(path, private_key)
                    oscscreen.notify_confirm(
                        "Private key successfully downloaded and stored in " + path, "Success!")
                    back()
                    return
            oscscreen.notify_confirm(
                "You must type a valid keypair name.", "Error!")
        global NAME
        NAME = self.add_widget(
            oscscreen.TitleText,
            name="Keypair's name:",
            value=NAME.get_value() if NAME else "")
        global VOLUME_COMBO
        self.add_widget(
            oscscreen.ButtonPress,
            name="CREATE").whenPressed = create
        self.add_widget(oscscreen.ButtonPress, name="EXIT").whenPressed = back
