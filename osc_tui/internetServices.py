from osc_tui import main
from osc_tui import popup 
from osc_tui import selectableGrid

class internetServicesGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id"]

        def on_selection(line):
            popup.selectInternetService(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadInternetServices(form=self.form)['InternetServices']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["InternetServiceId"])
        values = list()
        for g in groups:
            values.append([g['InternetServiceId']])
        self.values = values
