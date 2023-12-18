from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class nicsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "State", "SubnetId", "NetId", "Description", "MacAddress"]

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadNics(form=self.form)['Nics']
        return groups

    def refresh(self):
        nics = main.do_search(self.data.copy(), ["NicId", "State", "SubnetId", "NetId", "Description", "MacAddress"])
        values = list()
        for n in nics:
            subnet_id = n["SubnetId"] if "SubnetId" in n else "Unlinked"
            net_id = n["NetId"] if "NetId" in n else "Unlinked"
            description = n["Description"] if "Description" in n else "???"
            mac_address = n["MacAddress"] if "MacAddress" in n else "???"
            
            values.append([n['NicId'], n["State"], subnet_id, net_id, description, mac_address])
        self.values = values
