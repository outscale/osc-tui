from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class publicIpsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "Public Ip", "Vm Id"]

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadPublicIps(form=self.form)['PublicIps']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["PublicIpId", "PublicIp", "VmId"])
        values = list()
        for g in groups:
            VmId = g["VmId"] if "VmId" in g else "unattached"
            values.append([g['PublicIpId'], g["PublicIp"], VmId])
        self.values = values
