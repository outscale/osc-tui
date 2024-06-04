from osc_tui import main
from osc_tui import popup 
from osc_tui import selectableGrid

class nicsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "State", "SubnetId", "NetId", "Description", "MacAddress"]

        def on_selection(line):
            popup.selectNic(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadNics(form=self.form)['Nics']
        return groups

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            state = self.values[y][1]
            cell.highlight_whole_widget = True
            if state == "in-use":
                cell.color = "GOODHL"
            elif state == "available":
                cell.color = "CURSOR"
            else:
                cell.color = "RED_BLACK"

    def refresh(self):
        nics = main.do_search(self.data.copy(), ["NicId", "State", "SubnetId", "NetId", "Description", "MacAddress"])
        values = list()
        for n in nics:
            subnet_id = n["SubnetId"] if "SubnetId" in n else "Unlinked"
            net_id = n["NetId"] if "NetId" in n else "Unlinked"
            description = n["Description"] if "Description" in n else "???"
            mac_address = n["MacAddress"] if "MacAddress" in n else "???"
            
            values.append([n['NicId'], n["State"], subnet_id, net_id, description, mac_address])
        self.values = values
