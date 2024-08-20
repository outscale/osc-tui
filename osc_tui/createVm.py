import osc_npyscreen
from osc_tui import main
from osc_tui import preloader
import os

# If advanced VM creation enabled.
ADVANCED_MODE = True
# All images combo box.
IMG_COMBO = None
# List of all IDs
ID_LIST = None
# Textbox for name inpur.
NAME = None
# Key pairs combo box.
KEYPAIRS_COMBO = None
# All CPU
CPU = None
# Performance
PERFORMANCE = None
# Textbox for memory in gib
RAM_SIZE = None
# Textbox for disk in gib
DISK_SIZE = None
# Textbox for number of core
CORE = None
# List of all Subregions
REGION = None
# Action On Shutdown combo box.
AOS_COMBO = None
# security groups
SG = None
# Subnet
SUBNET = None

SUBNETS_IDS = []

SELECTED_SG = []

LIST_THRESHOLD = 6
POPUP_COLUMNS = 90

class OscCombo(osc_npyscreen.TitleCombo):
    def __init__(self, *args, **keywords):
        term_size = os.get_terminal_size()
        keywords["popup_columns"] = POPUP_COLUMNS
        keywords["popup_lines"] = 40
        keywords["popup_atx"] = int(term_size.columns / 2 - POPUP_COLUMNS /2)
        keywords["relx"] = LIST_THRESHOLD
        super().__init__(*args, **keywords)

class OscButtonPress(osc_npyscreen.ButtonPress):
    def __init__(self, *args, **keywords):
        keywords["popup_columns"] = POPUP_COLUMNS
        keywords["popup_lines"] = 40
        keywords["relx"] = LIST_THRESHOLD - 2
        super().__init__(*args, **keywords)

class CreateVm(osc_npyscreen.FormBaseNew):
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

        self.add_widget(osc_npyscreen.ButtonPress, name="SHOW " +
                        ("ADVANCED" if not ADVANCED_MODE else "BASIC") +
                        " SETTINGS", ).whenPressed = switchMode

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create_vmtype():
            cpu = CPU.get_values()[CPU.get_value()]
            perf = PERFORMANCE.get_values()[PERFORMANCE.get_value()]
            size = RAM_SIZE.get_value()
            core = CORE.get_value()
            if perf == "MEDIUM":
                performance = "3"
            if perf == "HIGH":
                performance = "2"
            if perf == "HIGHEST":
                performance = "1"
            vmtype = "tinav" + cpu[4] + ".c" + \
                core + "r" + size + "p" + performance
            return(vmtype)

        def create():

            if IMG_COMBO.get_value() is None or KEYPAIRS_COMBO.get_value() is None:
                osc_npyscreen.notify_confirm(
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
                    vmtype = create_vmtype()
                    sg = None
                    if len(SELECTED_SG) > 0:
                        sg = SELECTED_SG
                    disk_size = DISK_SIZE.get_value()
                    bdm = None
                    if disk_size != "Default":
                        bdm =  [
                            {
                                "DeviceName":"/dev/sda1",
                                "Bsu":{
                                    "VolumeSize": int(disk_size)
                                }
                            }
                        ]
                    subnet = None
                    if SUBNET.get_value() > 0:
                        subnet=SUBNETS_IDS[SUBNET.get_value() - 1]

                    res = main.GATEWAY.CreateVms(
                        form=self, ImageId=id, KeypairName=keypair, VmType=vmtype, Placement={
                            "SubregionName": REGION.get_values()[REGION.get_value()]
                        },
                        SecurityGroups=sg,
                        BlockDeviceMappings=bdm,
                        SubnetId=subnet,
                        VmInitiatedShutdownBehavior=AOS_COMBO.get_values()[AOS_COMBO.get_value()],
                    )
                else:
                    res = main.GATEWAY.CreateVms(
                        form=self,
                        Placement={
                            "SubregionName": REGION.get_values()[
                                REGION.get_value()]
                        },
                        ImageId=id, KeypairName=keypair)
                if res is None:
                    return
                elif "Errors" in res:
                    osc_npyscreen.notify_confirm(str(res["Errors"]))
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
            osc_npyscreen.TitleText,
            name="VM name:",
            relx=LIST_THRESHOLD,
            value=NAME.get_value() if NAME else "")
        global IMG_COMBO
        IMG_COMBO = self.add_widget(
            OscCombo,
            name="Image",
            values=imgs_vals,
            value=IMG_COMBO.get_value() if IMG_COMBO else 0,
        )
        global REGION
        subregions = preloader.Preloader.get('subregions')
        subregions_vals = []
        for subregion in subregions:
            subregions_vals.append(subregion["SubregionName"])
        REGION = self.add_widget(
            OscCombo,
            name="Region",
            values=subregions_vals,
            value=REGION.get_value() if REGION else 0,
        )
        global KEYPAIRS_COMBO
        KEYPAIRS_COMBO = self.add_widget(
            OscCombo,
            name="Keypair",
            values=keyPairsNames,
            value=KEYPAIRS_COMBO.get_value() if KEYPAIRS_COMBO else 0,
        )
        if ADVANCED_MODE:
            global SG

            def sgs_select_name():
                sg_select_name = "SGs("
                if len(SELECTED_SG) > 0:
                    for idx, sg in enumerate(SELECTED_SG):
                        if idx > 0:
                            sg_select_name += " "
                        sg_select_name += sg
                else:
                    sg_select_name += "default"
                # the space is because name isn't recalclate
                sg_select_name += ")                                                "
                return sg_select_name

            SGs_select = self.add_widget(
                OscButtonPress,
                name=sgs_select_name(),
            )
            def select_sgs():
                sgs = main.GATEWAY.ReadSecurityGroups(form=self)["SecurityGroups"]
                sg_vals = ["default"]
                for s in sgs:
                    if s["SecurityGroupName"] != "default":
                        sg_vals.append(s["SecurityGroupName"])
                class ConfirmCancelPopup(osc_npyscreen.fmPopup.ActionPopup):
                    term_size = os.get_terminal_size()
                    DEFAULT_COLUMNS = 100
                    DEFAULT_LINES = len(sg_vals) + 5
                    SHOW_ATX = int(term_size.columns / 2 - DEFAULT_COLUMNS /2)
                    def on_ok(self):
                        self.value = True

                    def on_cancel(self):
                        self.value = False

                popup = ConfirmCancelPopup(name="Select SGs")
                SG = popup.add_widget(
                    osc_npyscreen.MultiSelect,
                    name="SG",
                    values=sg_vals,
                    max_height=len(sg_vals) + 1,
                    scroll_exit=True,
                    width=30,
                    value=[0,],
                )
                def exit():
                    global SELECTED_SG
                    SELECTED_SG = []
                    for v_idx in SG.value:
                        SELECTED_SG.append(SG.values[v_idx])
                    popup.editing = False
                    SGs_select.name = sgs_select_name()

                popup.on_ok = exit
                popup.edit()
                self.display()

            SGs_select.whenPressed = select_sgs

            global CPU
            cpu_vals = "GEN 3|GEN 4|GEN 5|GEN 6".split("|")
            CPU = self.add_widget(
                OscCombo,
                name="Cpu",
                values=cpu_vals,
                value=CPU.get_value() if CPU else 3,
            )
            global SUBNET
            global SUBNETS_IDS
            SUBNETS_IDS = []
            subnet_read = main.GATEWAY.ReadSubnets(form=self)["Subnets"]
            subnet_vals = ["Default"]
            for sn in subnet_read:
                sn_id = sn["SubnetId"]
                name = sn_id
                if "Tags" in sn and len(sn["Tags"]) > 0 and sn["Tags"][0]["Key"] == "Name":
                    name = sn["Tags"][0]["Value"] + "(id :" + sn_id + ")"
                subnet_vals.append(name)
                SUBNETS_IDS.append(sn_id)
            SUBNET = self.add_widget(
                OscCombo,
                name="Subnet",
                values=subnet_vals,
                value=SUBNET.get_value() if SUBNET else 0,
            )

            global PERFORMANCE
            perf_vals = "MEDIUM HIGH HIGHEST".split(" ")
            PERFORMANCE = self.add_widget(
                OscCombo,
                name="Performance",
                values=perf_vals,
                value=PERFORMANCE.get_value() if PERFORMANCE else 0,
            )
            global RAM_SIZE
            RAM_SIZE = self.add_widget(
                osc_npyscreen.TitleText,
                relx=LIST_THRESHOLD,
                name="Ram(Gb)",
                value=RAM_SIZE.get_value() if RAM_SIZE else "2"
            )
            global DISK_SIZE
            DISK_SIZE = self.add_widget(
                osc_npyscreen.TitleText,
                relx=LIST_THRESHOLD,
                name="Disk(Gib)",
                value=DISK_SIZE.get_value() if DISK_SIZE else "Default"
            )
            global CORE
            CORE = self.add_widget(
                osc_npyscreen.TitleText,
                relx=LIST_THRESHOLD,
                name="number cores",
                value=CORE.get_value() if CORE else "1"
            )
            actionOnShutdown = "stop restart terminate".split(" ")
            global AOS_COMBO
            AOS_COMBO = self.add_widget(
                OscCombo,
                name="Stop Action",
                values=actionOnShutdown,
                value=AOS_COMBO.get_value() if AOS_COMBO else 0,
            )

        def creation():
            create()
            back()
        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="CREATE").whenPressed = creation
        self.add_widget(osc_npyscreen.ButtonPress, name="EXIT").whenPressed = back
