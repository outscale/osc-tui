from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class natServicesGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id"]

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadNatServices(form=self.form)['NatServices']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["NatServiceId"])
        values = list()
        for g in groups:
            values.append([g['NatServiceId']])
        self.values = values
