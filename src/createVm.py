import npyscreen
import main

TITLE_COMBO = None
ID_LIST = None
NAME = None
KEYPAIRS = None
KEYPAIRS_COMBO = None


class CreateVm(npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create():
            if TITLE_COMBO.get_value() == None or KEYPAIRS_COMBO.get_value() == None:
                npyscreen.notify_confirm(
                    "No image/keypair selected, please select one.",
                    title="Argument Missing",
                    form_color="STANDOUT",
                    wrap=True,
                    wide=False,
                )
                self.display()
                return
            else:
                id = ID_LIST[TITLE_COMBO.get_value()]
                keypair = KEYPAIRS[KEYPAIRS_COMBO.get_value()]
                res = main.GATEWAY.CreateVms(ImageId=id, KeypairName=keypair)
                vmId = res["Vms"][0]["VmId"]
                main.GATEWAY.CreateTags(
                    ResourceIds=[vmId],
                    Tags=[{"Key": "Name", "Value": NAME.get_value()}],
                )

        imgs = main.GATEWAY.ReadImages()["Images"]
        imgs_vals = []
        ID_LIST = []
        for img in imgs:
            account = img["AccountAlias"] if "AccountAlias" in img else "Unknow User"
            imgs_vals.append(
                "creator: "
                + account
                + " id: "
                + img["ImageId"]
                + " name: "
                + img["ImageName"]
            )
            ID_LIST.append(img["ImageId"])

        keyPairs = main.GATEWAY.ReadKeypairs()["Keypairs"]
        KEYPAIRS = []
        for keyPair in keyPairs:
            KEYPAIRS.append(keyPair["KeypairName"])
        NAME = self.add_widget(npyscreen.TitleText, name="VM name:")
        TITLE_COMBO = self.add_widget(
            npyscreen.TitleCombo, name="CHOOSE IMG", values=imgs_vals
        )
        KEYPAIRS_COMBO = self.add_widget(
            npyscreen.TitleCombo, name="CHOOSE KEYPAIR", values=KEYPAIRS
        )
        self.add_widget(npyscreen.ButtonPress, name="CREATE").whenPressed = create
        self.add_widget(npyscreen.ButtonPress, name="EXIT").whenPressed = back
