
import npyscreen
import pyperclip

from osc_tui import createVm
from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid
from osc_tui import virtualMachine


class VolumeGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "Type", 'Size (Gb)', 'Subregion', 'Linked To']

        def on_selection(line):
            popup.editVolume(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        groups = main.GATEWAY.ReadVolumes(form=self.form)['Volumes']
        values = list()
        for g in groups:
            VmId = g["LinkedVolumes"][0]["VmId"] if g["LinkedVolumes"] else "Unlinked"
            values.append([g["VolumeId"], g["VolumeType"],
                           g["Size"], g['SubregionName'], VmId])
        self.values = values


class VolumeGridForOneInstance(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "Name", 'Size (Gb)', 'Subregion']

        def on_selection(line):
            pass

        self.on_selection = on_selection

    def refresh(self):
        id = main.VM["VmId"]
        volume = main.GATEWAY.ReadVolumes(
            form=self.form, Filters={
                'LinkVolumeVmIds': [id]})
        groups = volume['Volumes']
        values = list()
        for g in groups:
            values.append([g["VolumeId"], g["VolumeType"],
                           g["Size"], g['SubregionName']])
        self.values = values
