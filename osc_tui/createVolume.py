import osc_npyscreen

from osc_tui import main

# All images combo box.
SNAPSHOT_COMBO = None
# List of all IDs
ID_LIST = None
# Textbox for name inpur.
NAME = None
# TYPE of volume
TYPE = None
# SUBREGION name
SUBREGION = None
# SIZE of volume in gib
SIZE = None


class CreateVolume(osc_npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("CREATE_VOLUME", CreateVolume, name="osc-tui")
        self.parentApp.switchForm("CREATE_VOLUME")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create():

            if SNAPSHOT_COMBO.get_value() is None or SUBREGION.get_value() is None:
                osc_npyscreen.notify_confirm(
                    "No snapshot/subregion selected, please select one.",
                    title="Argument Missing",
                    form_color="STANDOUT",
                    wrap=True,
                    wide=False,
                )
                self.display()
                return
            else:
                id = ID_LIST[SNAPSHOT_COMBO.get_value()]
                subregionName = SUBREGION.get_values()[
                    SUBREGION.get_value()
                ]
                volumeType = TYPE.get_values()[
                    TYPE.get_value()
                ]
                res = main.GATEWAY.CreateVolume(
                    form=self,
                    SnapshotId=id,
                    SubregionName=subregionName,
                    Size=int(SIZE.get_value()),
                    VolumeType=volumeType
                )
                if "Errors" in res:
                    osc_npyscreen.notify_confirm(str(res["Errors"]))
                else:
                    volumeId = res["Volume"]["VolumeId"]
                    main.GATEWAY.CreateTags(
                        form=self,
                        ResourceIds=[volumeId],
                        Tags=[{"Key": "Name", "Value": NAME.get_value()}],
                    )
                back()

        snapshots = main.GATEWAY.ReadSnapshots(form=self)["Snapshots"]
        snapshots_vals = ["None"]
        ID_LIST = [None]
        for snap in snapshots:
            name = snap["Tags"][0]["Value"] if snap["Tags"] else "Unkown"
            snapshots_vals.append(
                " id: " + snap["SnapshotId"] + " name: " + name
            )
            ID_LIST.append(snap["SnapshotId"])

        global NAME
        NAME = self.add_widget(
            osc_npyscreen.TitleText,
            name="Volume name:",
            value=NAME.get_value() if NAME else "")
        global SNAPSHOT_COMBO
        SNAPSHOT_COMBO = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="CHOOSE SNAPSHOT",
            values=snapshots_vals,
            value=SNAPSHOT_COMBO.get_value() if SNAPSHOT_COMBO else 0,
        )
        global TYPE
        TYPE = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="CHOOSE A TYPE",
            values=["standard", "io1", "gp2"],
            value=TYPE.get_value() if TYPE else 0,
        )
        global SUBREGION
        subregions = main.GATEWAY.ReadSubregions(form=self)["Subregions"]
        subregions_vals = []
        for subregion in subregions:
            subregions_vals.append(subregion["SubregionName"])
        SUBREGION = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="CHOOSE A SUBREGION",
            values=subregions_vals,
            value=SUBREGION.get_value() if SUBREGION else 0
        )
        global SIZE
        SIZE = self.add_widget(
            osc_npyscreen.TitleText,
            name="CHOOSE A SIZE (gib)",
            value=SIZE.get_value() if SIZE else "10"
        )

        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="CREATE").whenPressed = create
        self.add_widget(osc_npyscreen.ButtonPress, name="EXIT").whenPressed = back
