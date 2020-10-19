import npyscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine


class loadbalancerGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Name", "Type", "DNS name"]

        def on_selection(line):
            popup.editLoadbalancer(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        groups = main.GATEWAY.ReadLoadBalancers(form=self.form)[
            'LoadBalancers']
        values = list()
        for g in groups:
            values.append([g['LoadBalancerName'], g['LoadBalancerType'],
                           g['DnsName']])
        self.values = values
