from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class nicsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "State"]

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadNics(form=self.form)['Nics']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["NicId", "State"])
        values = list()
        for g in groups:
            values.append([g['NicId'], g["State"]])
        self.values = values
