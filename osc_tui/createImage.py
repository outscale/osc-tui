import osc_npyscreen
from osc_tui import main

# All images combo box.
SNAPSHOT_COMBO = None
# List of all IDs
ID_LIST = None
# Textbox for name inpur.
NAME = None
# All vm combo box
VM_COMBO = None
# All architecture combo
ARCHITECTURE = None
# Choose reboot VM
REBOOT=None

class CreateImage_frominstance(osc_npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("CREATEIMAGE_FROMINSTANCE", CreateImage_frominstance, name="osc-tui")
        self.parentApp.switchForm("CREATEIMAGE_FROMINSTANCE")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.addForm("CREATE_IMAGE", CreateImage, name="osc-tui")
            self.parentApp.switchForm("CREATE_IMAGE")

        def back_cockpit():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        def create():

            if VM_COMBO.get_value() is None:
                osc_npyscreen.notify_confirm(
                    "No instance selected, please select one.",
                    title="Argument Missing",
                    form_color="STANDOUT",
                    wrap=True,
                    wide=False,
                )
                self.display()
                return
            else:
                id = VM_list[VM_COMBO.get_value()]
                name = NAME.get_value()
                if REBOOT.get_value() == 1:
                    reboot=True
                else:
                    reboot=False
                res = main.GATEWAY.CreateImage(
                    VmId=id,
                    ImageName=name,
                    NoReboot=reboot,
                )
                if "Errors" in res:
                    osc_npyscreen.notify_confirm(str(res["Errors"]))
                back_cockpit()

        vms = main.GATEWAY.ReadVms(form=self)["Vms"]
        vms_vals = []
        VM_list = []
        for vm in vms:
            name = vm["Tags"][0]["Value"] if vm["Tags"] else "Unkown"
            vms_vals.append(
                " id: " + vm["VmId"] + " name: " + name
            )
            VM_list.append(vm["VmId"])
        global NAME
        NAME = self.add_widget(
            osc_npyscreen.TitleText,
            name="Image name:",
            value=NAME.get_value() if NAME else "")
        global VM_COMBO
        VM_COMBO = self.add_widget(
                osc_npyscreen.TitleCombo,
                name="ORIGINAL VM",
                values=vms_vals,
                value=VM_COMBO.get_value() if VM_COMBO else 0,
            )
        global REBOOT
        REBOOT = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="REBOOT",
            values=["true", "false"],
            value=REBOOT.get_value() if REBOOT else 0,
        )
        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="CREATE").whenPressed = create
        self.add_widget(osc_npyscreen.ButtonPress, name="EXIT").whenPressed = back

class CreateImage_fromsnapshot(osc_npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("CREATEIMAGE_FROMSNAPSHOT", CreateImage_fromsnapshot, name="osc-tui")
        self.parentApp.switchForm("CREATEIMAGE_FROMSNAPSHOT")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.addForm("CREATE_IMAGE", CreateImage, name="osc-tui")
            self.parentApp.switchForm("CREATE_IMAGE")

        def back_cockpit():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        def create():

            if SNAPSHOT_COMBO.get_value() is None:
                osc_npyscreen.notify_confirm(
                    "No snapshot selected, please select one.",
                    title="Argument Missing",
                    form_color="STANDOUT",
                    wrap=True,
                    wide=False,
                )
                self.display()
                return
            else:
                id = ID_LIST[SNAPSHOT_COMBO.get_value()]
                if ARCHITECTURE.get_value() == 1:
                    archi = "x86_64"
                else:
                    archi = "i386"
                name = NAME.get_value()
                res = main.GATEWAY.CreateImage(ImageName=name
                ,BlockDeviceMappings=[{"Bsu": {"SnapshotId": id}, "DeviceName": "/dev/sda1"}]
                ,RootDeviceName="/dev/sda1", Architecture=archi)
                if "Errors" in res:
                    osc_npyscreen.notify_confirm(str(res["Errors"]))
                back_cockpit()

        snapshots = main.GATEWAY.ReadSnapshots(form=self)["Snapshots"]
        snapshots_vals = []
        ID_LIST = []
        for snap in snapshots:
            name = snap["Tags"][0]["Value"] if snap["Tags"] else "Unkown"
            snapshots_vals.append(
                " id: " + snap["SnapshotId"] + " name: " + name
            )
            ID_LIST.append(snap["SnapshotId"])
        global NAME
        NAME = self.add_widget(
            osc_npyscreen.TitleText,
            name="Image name:",
            value=NAME.get_value() if NAME else "")
        global SNAPSHOT_COMBO
        SNAPSHOT_COMBO = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="ORIGINAL SNAPSHOT",
            values=snapshots_vals,
            value=SNAPSHOT_COMBO.get_value() if SNAPSHOT_COMBO else 0,
        )
        global ARCHITECTURE
        ARCHITECTURE = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="ARCHITECTURE",
            values=["i386", "x86_64"],
            value=ARCHITECTURE.get_value() if ARCHITECTURE else 0,
        )
        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="CREATE").whenPressed = create
        self.add_widget(osc_npyscreen.ButtonPress, name="EXIT").whenPressed = back

class CreateImage(osc_npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("CREATE_IMAGE", CreateImage, name="osc-tui")
        self.parentApp.switchForm("CREATE_IMAGE")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        def switch_fromsnapshot():
            self.parentApp.addForm("CREATEIMAGE_FROMSNAPSHOT", CreateImage_fromsnapshot, name="osc-tui")
            self.parentApp.switchForm("CREATEIMAGE_FROMSNAPSHOT")

        def switch_frominstance():
            self.parentApp.addForm("CREATEIMAGE_FROMINSTANCE", CreateImage_frominstance, name="osc-tui")
            self.parentApp.switchForm("CREATEIMAGE_FROMINSTANCE")

        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="Create from snapshot").whenPressed=switch_fromsnapshot
        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="Create from vms").whenPressed = switch_frominstance
        self.add_widget(osc_npyscreen.ButtonPress, name="EXIT").whenPressed = back