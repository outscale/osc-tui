from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class natServicesGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "State", "NetId", "SubnetId"]

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadNatServices(form=self.form)['NatServices']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["NatServiceId", "State", "NetId", "SubnetId"])
        values = list()
        for g in groups:
            values.append([g['NatServiceId'], g['State'],
                           g["NetId"] if "NetId" in g else "unliked",
                           g["SubnetId"] if "SubnetId" in g else "unliked"])
        self.values = values
