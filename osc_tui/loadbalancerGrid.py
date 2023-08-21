from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid


class loadbalancerGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Name", "Type", "DNS name"]

        def on_selection(line):
            main.LBU = line[0]
            popup.editLoadbalancer(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadLoadBalancers(form=self.form)
        if groups is None:
            return None
        return groups['LoadBalancers']

    def refresh(self):
        main.LBUs = list()
        self.values = list()
        groups = main.do_search(self.data.copy(), ['LoadBalancerName', 'LoadBalancerType',
                                                   'DnsName'])
        if groups is not None:
            main.LBUs = groups
            values = list()
            for g in groups:
                values.append([g['LoadBalancerName'], g['LoadBalancerType'],
                               g['DnsName']])
            self.values = values
