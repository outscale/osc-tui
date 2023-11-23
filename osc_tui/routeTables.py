from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class routeTablesGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id"]

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadRouteTables(form=self.form)['RouteTables']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["RouteTableId"])
        values = list()
        for g in groups:
            values.append([g['RouteTableId']])
        self.values = values
