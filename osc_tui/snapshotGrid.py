from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid


class SnapshotGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "Description", "Size (Gb)", "Volume"]

        def on_selection(line):
            popup.editSnapshot(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        return main.GATEWAY.ReadSnapshots(form=self.form)['Snapshots']

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["SnapshotId", "Description",
                                                   "VolumeId", "VolumeSize"])
        values = list()
        for g in groups:
            vId = g['VolumeId'] if 'VolumeId' in g else "no volumes"
            vSize = g['VolumeSize'] if 'VolumeSize' in g else "unknow"
            values.append([g['SnapshotId'], g['Description'], vSize, vId])
        self.values = values
