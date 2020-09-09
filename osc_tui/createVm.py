import npyscreen
import main
import preloader

# If advanced VM creation enabled.
ADVANCED_MODE = False
# All images combo box.
IMG_COMBO = None
# List of all IDs
ID_LIST = None
# Textbox for name inpur.
NAME = None
# Key pairs combo box.
KEYPAIRS_COMBO = None
# VM TYPE combo box.
VM_COMBO = None
REGION = None
# Action On Shutdown combo box.
AOS_COMBO = None


class CreateVm(npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("CREATE_VM", CreateVm, name="osc-tui")
        self.parentApp.switchForm("CREATE_VM")

    def create(self):
        preloader.Preloader.wait_for_preload(self)

        def switchMode():
            global ADVANCED_MODE
            ADVANCED_MODE = not ADVANCED_MODE
            self.reload()

        self.add_widget(npyscreen.ButtonPress, name="SHOW " +
                        ("ADVANCED" if not ADVANCED_MODE else "BASIC") +
                        " SETTINGS", ).whenPressed = switchMode

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create():

            if IMG_COMBO.get_value() is None or KEYPAIRS_COMBO.get_value() is None:
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
                id = ID_LIST[IMG_COMBO.get_value()]
                keypair = KEYPAIRS_COMBO.get_values()[
                    KEYPAIRS_COMBO.get_value()]
                res = ""
                if ADVANCED_MODE:
                    res = main.GATEWAY.CreateVms(
                        form=self, ImageId=id, KeypairName=keypair, VmType=VM_COMBO.get_values()[
                            VM_COMBO.get_value()], Placement={
                            "SubregionName": REGION.get_values()[
                                REGION.get_value()]}, VmInitiatedShutdownBehavior=AOS_COMBO.get_values()[
                            AOS_COMBO.get_value()], )
                else:
                    res = main.GATEWAY.CreateVms(
                        form=self,
                        ImageId=id, KeypairName=keypair)
                if "Errors" in res:
                    npyscreen.notify_confirm(str(res["Errors"]))
                else:
                    vmId = res["Vms"][0]["VmId"]
                    main.GATEWAY.CreateTags(
                        form=self,
                        ResourceIds=[vmId],
                        Tags=[{"Key": "Name", "Value": NAME.get_value()}],
                    )
        imgs = preloader.Preloader.get('vm_images')
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

        keyPairs = main.GATEWAY.ReadKeypairs(form=self)["Keypairs"]
        keyPairsNames = []
        for keyPair in keyPairs:
            keyPairsNames.append(keyPair["KeypairName"])
        global NAME
        NAME = self.add_widget(
            npyscreen.TitleText,
            name="VM name:",
            value=NAME.get_value() if NAME else "")
        global IMG_COMBO
        IMG_COMBO = self.add_widget(
            npyscreen.TitleCombo,
            name="CHOOSE IMG",
            values=imgs_vals,
            value=IMG_COMBO.get_value() if IMG_COMBO else 0,
        )
        global REGION
        subregions = preloader.Preloader.get('subregions')
        subregions_vals = []
        for subregion in subregions:
            subregions_vals.append(subregion["SubregionName"])
        REGION = self.add_widget(
            npyscreen.TitleCombo,
            name="CHOOSE REGION",
            values=subregions_vals,
            value=REGION.get_value() if REGION else 0,
        )
        global KEYPAIRS_COMBO
        KEYPAIRS_COMBO = self.add_widget(
            npyscreen.TitleCombo,
            name="CHOOSE KEYPAIR",
            values=keyPairsNames,
            value=KEYPAIRS_COMBO.get_value() if KEYPAIRS_COMBO else 0,
        )
        if ADVANCED_MODE:
            vmTypes = preloader.Preloader.get('vm_types')
            vmTypes_vals = []
            for vmType in vmTypes:
                vmTypes_vals.append(vmType["VmTypeName"])
            global VM_COMBO
            VM_COMBO = self.add_widget(
                npyscreen.TitleCombo,
                name="CHOOSE VM TYPE",
                values=vmTypes_vals,
                value=VM_COMBO.get_value() if VM_COMBO else 0,
            )
            actionOnShutdown = "stop restart terminate".split(" ")
            global AOS_COMBO
            AOS_COMBO = self.add_widget(
                npyscreen.TitleCombo,
                name="ACTION ON SHUTDOWN",
                values=actionOnShutdown,
                value=AOS_COMBO.get_value() if AOS_COMBO else 0,
            )

        def creation():
            create()
            back()
        self.add_widget(
            npyscreen.ButtonPress,
            name="CREATE").whenPressed = creation
        self.add_widget(npyscreen.ButtonPress, name="EXIT").whenPressed = back
