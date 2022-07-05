import oscscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine


class vpcsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "CIDR", "DHCP Options Id"]

        def on_selection(line):
            popup.editVpcs(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadNets(form=self.form)['Nets']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["NetId", "IpRange",
                                                   "DhcpOptionsSetId"])
        values = list()
        for g in groups:
            values.append([g['NetId'],
                           g['IpRange'], g['DhcpOptionsSetId']])
        self.values = values


class subnetGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "CIDR", "NET ID"]

        def on_selection(line):
            popup.editSubnet(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadSubnets(
            Filters={"NetIds": [popup.SUBNETID]})['Subnets']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["SubnetId", "IpRange", "NetId"])
        values = list()
        for g in groups:
            values.append([g['SubnetId'],
                           g['IpRange'], g['NetId']])
        self.values = values
