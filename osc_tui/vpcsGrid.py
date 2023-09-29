from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid


class vpcsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "CIDR", "DHCP Options Id", "State"]

        def on_selection(line):
            popup.editVpcs(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadNets(form=self.form)['Nets']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["NetId", "IpRange",
                                                   "DhcpOptionsSetId", "State"])
        values = list()
        for g in groups:
            values.append([g['NetId'], g['IpRange'], g['DhcpOptionsSetId'],
                           g["State"]])
        self.values = values


class subnetGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "CIDR", "Net ID", "State"]

        def on_selection(line):
            popup.editSubnet(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadSubnets(
            Filters={"NetIds": [popup.SUBNETID]})['Subnets']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["SubnetId", "IpRange", "NetId", "State"])
        values = list()
        for g in groups:
            values.append([g['SubnetId'],
                           g['IpRange'], g['NetId'], g['State']])
        self.values = values
