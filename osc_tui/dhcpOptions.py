from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class dhcpOptionsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id"]
        
        def on_selection(line):
            popup.editDhcpOptions(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadDhcpOptions(form=self.form)['DhcpOptionsSets']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["DhcpOptionsSetId"])
        values = list()
        for g in groups:
            values.append([g['DhcpOptionsSetId']])
        self.values = values
