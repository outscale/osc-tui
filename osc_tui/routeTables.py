from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class routeTablesGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "NetId"]

        def on_selection(line):
            popup.selectRouteTable(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadRouteTables(form=self.form)['RouteTables']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["RouteTableId", "NetId"])
        values = list()
        for g in groups:
            values.append([g['RouteTableId'], g["NetId"] if "NetId" in g else "No Net"])
        self.values = values
