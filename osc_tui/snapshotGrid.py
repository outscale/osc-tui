import npyscreen
import pyperclip

from osc_tui import createVm
from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid
from osc_tui import virtualMachine


class SnapshotGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "Description", "Size (Gb)", "Volume"]

        def on_selection(line):
            popup.editSnapshot(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        groups = main.GATEWAY.ReadSnapshots(form=self.form)['Snapshots']
        values = list()
        for g in groups:
            values.append([g['SnapshotId'], g['Description'],
                           g['VolumeSize'], g['VolumeId']])
        self.values = values
