from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class publicIpsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "Public Ip", "Vm Id"]

        def on_selection(line):
            popup.selectPublicIp(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadPublicIps(form=self.form)['PublicIps']
        return groups

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            linkto = self.values[y][2]
            cell.highlight_whole_widget = True
            if linkto == "unattached":
                cell.color = "CURSOR"
            else:
                cell.color = "GOODHL"

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["PublicIpId", "PublicIp", "VmId"])
        values = list()
        for g in groups:
            VmId = g["VmId"] if "VmId" in g else "unattached"
            values.append([g['PublicIpId'], g["PublicIp"], VmId])
        self.values = values
