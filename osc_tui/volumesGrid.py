
import npyscreen
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
