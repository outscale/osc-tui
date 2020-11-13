import npyscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine

class vpcsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "CIDR", "DHCP Options ID"]

        def on_selection(line):
            popup.editVpcs(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        groups = main.GATEWAY.ReadNets(form=self.form)[
            'Nets']
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

    def refresh(self):
        groups = main.GATEWAY.ReadSubnets(Filters={"NetIds": [popup.SUBNETID]})[
            'Subnets']
        values = list()
        for g in groups:
            values.append([g['SubnetId'],
                           g['IpRange'], g['NetId']])
        self.values = values
