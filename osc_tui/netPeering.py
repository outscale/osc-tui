from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class Grid(selectableGrid.SelectableGrid):
    def __init__(self, screen,  *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "AccepterNet", "State"]

        def on_selection(line):
            popup.editNetPeering(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        return main.GATEWAY.ReadNetPeerings(form=self.form)['NetPeerings']

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            state = self.values[y][2]
            cell.highlight_whole_widget = True
            # states: pending-acceptance | active | rejected | failed | expired | deleted
            if state == "active":
                cell.color = "GOODHL"
            elif state == "pending-acceptance":
                cell.color = "CURSOR"
            else:
                cell.color = "DANGER"

    def refresh(self):
        groups = main.do_search(self.data.copy(), ['NetPeeringId'], state_msg=True, accepted_net=True)

        values = list()
        for g in groups:
            AccepterNet = g["AccepterNet"]
            AccepterNetId = AccepterNet["NetId"] if AccepterNet else "Not Accepted"
            values.append([g['NetPeeringId'], AccepterNetId, g['State']['Message']])
        self.values = values
