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

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            state = self.values[y][3]
            # states: pending | available | deleted
            cell.highlight_whole_widget = True
            if state == "available":
                cell.color = "GOODHL"
            elif state == "deleted":
                cell.color = "DANGER"
            else:
                cell.color = "RED_BLACK"

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
        self.col_titles = ["ID", "Name", "CIDR", "Net ID", "State"]

        def on_selection(line):
            popup.editSubnet(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadSubnets(
            Filters={"NetIds": [popup.SUBNETID]})['Subnets']
        return groups

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            state = self.values[y][4]
            # states: pending | available | deleted
            cell.highlight_whole_widget = True
            if state == "available":
                cell.color = "GOODHL"
            elif state == "deleted":
                cell.color = "DANGER"
            else:
                cell.color = "RED_BLACK"

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["SubnetId", "IpRange", "NetId", "State"],
                                name_as_tag=True)
        values = list()
        for g in groups:
            name="No Name"
            if "Tags" in g and len(g["Tags"]) > 0 and g["Tags"][0]["Key"] == "Name":
                name = g["Tags"][0]["Value"]

            values.append([g['SubnetId'], name,
                           g['IpRange'], g['NetId'], g['State']])
        self.values = values
