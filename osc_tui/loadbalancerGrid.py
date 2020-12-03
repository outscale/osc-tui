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
            main.LBU = line[0]
            popup.editLoadbalancer(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        main.LBUs = list()
        self.values = list()
        groups = main.GATEWAY.ReadLoadBalancers(form=self.form)
        if 'LoadBalancers' in groups:
            groups = groups['LoadBalancers']
            main.LBUs = groups
            values = list()
            for g in groups:
                values.append([g['LoadBalancerName'], g['LoadBalancerType'],
                               g['DnsName']])
            self.values = values
