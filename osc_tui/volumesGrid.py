
import oscscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine


class VolumeGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = [
            "Id",
            "Type",
            'Size (Gb)',
            'Subregion',
            'Linked To',
            "Device Name"]

        def on_selection(line):
            popup.editVolume(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadVolumes(form=self.form)
        if groups is None:
            return None
        return groups['Volumes']

    def refresh(self):
        groups = main.do_search(self.data.copy(), ['VolumeId', 'VolumeType',
                                                   'Size', 'SubregionName'])
        values = list()
        for g in groups:
            VolLink = g["LinkedVolumes"]
            VmId = VolLink[0]["VmId"] if VolLink else "Unlinked"
            DName = VolLink[0]["DeviceName"] if VolLink else "No Dev Today"
            values.append([g["VolumeId"], g["VolumeType"],
                           g["Size"], g['SubregionName'], VmId, DName])
        self.values = values


class VolumeEdit(oscscreen.FormBaseNew):
    volume=None
    size=10
    size_wid=None
    LIST_THRESHOLD=4

    def __init__(self, *args, **keywords):
        self.volume = keywords["volume"]
        self.size = self.volume[2]
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("Volumes-Edit", CreateVolume, name="osc-tui")
        self.parentApp.switchForm("Volumes-Edit")

    def back(self):
        main.kill_threads()
        self.parentApp.switchForm("Cockpit")

    def update(self):
        id=self.volume[0]
        main.GATEWAY.UpdateVolume(VolumeId=id,
                                  Size=int(self.size_wid.get_value()))
        self.back()

    def create(self):

        self.size_wid = self.add_widget(
            oscscreen.TitleText,
            relx=self.LIST_THRESHOLD,
            name="size",
            value=str(self.size)
        )

        self.add_widget(oscscreen.ButtonPress,
                        name="UPDATE").whenPressed = self.update
        self.add_widget(oscscreen.ButtonPress,
                        name="EXIT").whenPressed = self.back



class VolumeGridForOneInstance(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "Name", 'Size (Gb)', 'Subregion']

        def on_selection(line):
            pass

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        id = main.VM["VmId"]
        groups = main.GATEWAY.ReadVolumes(
            form=self.form, Filters={
                'LinkVolumeVmIds': [id]})
        if groups is None:
            return None
        return groups['Volumes']


    def refresh(self):
        id = main.VM["VmId"]
        groups = main.do_search(self.data.copy(), ['VolumeId', 'VolumeType',
                                                   'Size', 'SubregionName'])
        values = list()
        for g in groups:
            values.append([g["VolumeId"], g["VolumeType"],
                           g["Size"], g['SubregionName']])
        self.values = values
