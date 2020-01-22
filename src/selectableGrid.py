import curses
import threading
import time

import npyscreen

import main

# Initially it was designed to have a thread that auto refresh... However, even if it worked fine, if too many people does it, it looks like a DDOS attack.
# So now, use [F5] key to refreesh, a find a button called refresh.

class SelectableGrid(npyscreen.GridColTitles):
    def __init__(self, screen, form, on_selection=None, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.scroll_exit = True
        self.on_selection = on_selection
        self.selected_row = 0
        self.t1 = self.time()
        self.t2 = self.time()
        self.time_without_refreshing = 0
        self.exit_left = True
        self.exit_right = True
        self.form = form

    def set_up_handlers(self):
        super().set_up_handlers()
        self.add_handlers({10: self.exit_enter})
        self.add_handlers({curses.KEY_F5: self.h_refresh})

    def time(self):
        return int(round(time.time() * 1000))

    def h_refresh(self, inpt):
        self.refresh()
        self.display()

    # Each time we change the selected line, we select the new one.
    def h_move_line_down(self, inpt):
        super().h_move_line_down(inpt)
        # self.select(inpt)

    def h_move_line_up(self, inpt):
        selected_row = self.edit_cell[0]
        super().h_move_line_up(inpt)
        # self.select(inpt)
        selected_row += self.edit_cell[0]
        # Means we are hitting the top of the widget.
        if selected_row == 0:
            self.h_exit_up(inpt)

    def h_move_cell_left(self, inpt):
        if len(self.values) > 0:
            if self.edit_cell[0] >= len(self.values):
                self.edit_cell[0] = len(self.values)  - 1
            if self.edit_cell[1] > self.columns:
                self.edit_cell[1] -= (self.columns + 1)
                self.edit_cell[1] = self.edit_cell[1] if self.edit_cell[1]>0 else 0
                if self.edit_cell[1] < self.begin_col_display_at:
                    self.h_scroll_left(inpt)
                if self.edit_cell[1] < self.columns:
                    self.edit_cell[1] = 0
            else:
                self.h_exit_up(inpt)

    def h_move_cell_right(self, inpt):
        if len(self.values) > 0:
            if self.edit_cell[0] >= len(self.values):
                self.edit_cell[0] = len(self.values)  - 1
            if self.edit_cell[1] <= len(self.values[self.edit_cell[0]]) -2:   # Only allow move to end of current line
                self.edit_cell[1] += self.columns
                self.edit_cell[1] = self.edit_cell[1] if self.edit_cell[1]<len(self.values) else len(self.values) - 1
                if self.edit_cell[1] > self.begin_col_display_at + self.columns-1:
                    self.h_scroll_right(inpt)

    def exit_enter(self, input):
        self.select(input)
        # On Enter, we also exit the widget.
        self.h_exit(input)

    def h_exit_mouse(self, _input):
        super().h_exit_mouse(_input)
        # Allow mouse selection.
        self.select(_input)

    def select(self, inpt=None):
        if(self.edit_cell):
            self.selected_row = self.edit_cell[0]
            if self.on_selection != None:
                if not self.selected_row < len(self.values):
                    self.selected_row = len(self.values) - 1
                if self.selected_row < 0:
                    self.selected_row = 0
                self.on_selection(self.values[self.selected_row])

    # Call this func to enable self-refresh of the screen.
    def start_updater(self):
        if main.POLL_ENABLED:
            self.updater = GridUpdater(self)
            main.add_thread(self.updater)
            self.updater.start()

    # The func to override in order to refresh the screen.
    def refresh(self):
        pass

# This is the component that will poll the server and refresh the grid once started.


class GridUpdater(threading.Thread):
    def __init__(self, grid, period=2000):
        threading.Thread.__init__(self)
        self.grid = grid
        self.t1 = self.grid.time()
        self.t2 = self.grid.time()
        self.timeSinceLastRefresh = 0
        self.period = period
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running == True:
            self.t2 = self.grid.time()
            dt = self.t2 - self.t1
            self.timeSinceLastRefresh += dt
            if self.timeSinceLastRefresh > self.period:
                self.grid.refresh()
                if self.running:
                    self.grid.display()
                self.timeSinceLastRefresh = 0
                self.grid.select()
            time.sleep(0.5)
