import threading
import time

import npyscreen


class SelectableGrid(npyscreen.GridColTitles):

    def __init__(self, screen, on_selection=None, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.scroll_exit = True
        self.on_selection = on_selection
        self.selected_row = 0
        self.t1 = int(round(time.time() * 1000))
        self.t2 = int(round(time.time() * 1000))
        self.time_without_refreshing = 0

    def set_up_handlers(self):
        super().set_up_handlers()
        self.add_handlers({10: self.exit_enter})

    # Each time we change the selected line, we select the new one.
    def h_move_line_down(self, inpt):
        super().h_move_line_down(inpt)
        self.select(inpt)

    def h_move_line_up(self, inpt):
        super().h_move_line_up(inpt)
        self.select(inpt)

    def exit_enter(self, input):
        self.select(input)
        # On Enter, we also exit the widget.
        self.h_exit(input)

    def h_exit_mouse(self, _input):
        super().h_exit_mouse(_input)
        # Allow mouse selection.
        self.select(_input)

    def select(self, inpt=None):
        self.selected_row = self.edit_cell[0]
        if self.on_selection != None:
            self.on_selection(self.values[self.selected_row])

    def custom_print_cell(self, cell, cell_value):
        if not isinstance(cell.grid_current_value_index, int):
            y, x = cell.grid_current_value_index
            status = self.values[y][0]
            cell.highlight_whole_widget = True
            if status == 'running':
                cell.color = 'GOODHL'
            elif status == 'pending':
                cell.color = 'RED_BLACK'
            elif status == 'stopping':
                cell.color = 'RED_BLACK'
            elif status == 'stopped':
                cell.color = 'CURSOR'
