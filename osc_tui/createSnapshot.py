import osc_npyscreen
from osc_tui import main

# All VOLUME_COMBO box.
VOLUME_COMBO = None
# List of all IDs
ID_LIST = None
# NAME inpur.
NAME = None
# DESCRIPTION of Snapshot
DESCRIPTION = None


class CreateSnapshot(osc_npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm(
            "CREATE_SNAPSHOT",
            CreateSnapshot,
            name="osc-tui")
        self.parentApp.switchForm("CREATE_SNAPSHOT")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create():

            if VOLUME_COMBO.get_value() is None:
                osc_npyscreen.notify_confirm(
                    "No volume selected, please select one.",
                    title="Argument Missing",
                    form_color="STANDOUT",
                    wrap=True,
                    wide=False,
                )
                self.display()
                return
            else:
                id = ID_LIST[VOLUME_COMBO.get_value()]
                res = main.GATEWAY.CreateSnapshot(
                    form=self,
                    VolumeId=id,
                    Description=DESCRIPTION.get_value(),
                )
                if "Errors" in res:
                    osc_npyscreen.notify_confirm(str(res["Errors"]))
                else:
                    snapshotId = res["Snapshot"]["SnapshotId"]
                    main.GATEWAY.CreateTags(
                        form=self,
                        ResourceIds=[snapshotId],
                        Tags=[{"Key": "Name", "Value": NAME.get_value()}],
                    )
                back()

        volumes = main.GATEWAY.ReadVolumes(form=self)["Volumes"]
        volumes_vals = []
        ID_LIST = []
        for volume in volumes:
            name = volume["Tags"][0]["Value"] if volume["Tags"] else "Unkown"
            volumes_vals.append(
                " id: " + volume["VolumeId"] + " name: " + name
            )
            ID_LIST.append(volume["VolumeId"])

        global NAME
        NAME = self.add_widget(
            osc_npyscreen.TitleText,
            name="Snapshot name:",
            value=NAME.get_value() if NAME else "")
        global VOLUME_COMBO
        VOLUME_COMBO = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="CHOOSE VOLUME",
            values=volumes_vals,
            value=VOLUME_COMBO.get_value() if VOLUME_COMBO else 0,
        )
        global DESCRIPTION
        DESCRIPTION = self.add_widget(
            osc_npyscreen.TitleText,
            name="Snapshot description:",
            value=DESCRIPTION.get_value() if DESCRIPTION else ""
        )
        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="CREATE").whenPressed = create
        self.add_widget(osc_npyscreen.ButtonPress, name="EXIT").whenPressed = back
