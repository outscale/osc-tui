import npyscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine


class SnapshotGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.col_titles = ["ID", "Name", "Description", "Owner Id", "Size (Gb)", "Volume"]

        def on_selection(line):
            print("ON_SELECTION")
#            popup.editSnapshot(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        groups = main.GATEWAY.ReadSnapshots()['Snapshots']
        values = list()
        print("REFRESH")
        for g in groups:
            print(g)
            name = g['Tags'][0]['Value'] if g['Tags'][0] else "Unknown"
            values.append([g['AccountId'], g['SnapshotId'], g['Description'], g['VolumeSize'], g['VolumeId'], name])
        print(values)
        self.values = values
