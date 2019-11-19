import curses

import npyscreen

import vmGrid
import vmInspector


class CockpitForm(npyscreen. FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        y, x = self.useable_space()
        self.draw_line_at = int(y/2)
        a = None

        def on_selection(line):
            a.set_value(line)
        vmGrid.add_vm_browser(self, on_selection)
        a = vmInspector.add_vm_inspector(self)

    def draw_form(self,):
        MAXY, MAXX = self.curses_pad.getmaxyx()
        super(CockpitForm, self).draw_form()
        self.curses_pad.hline(self.draw_line_at, 1, curses.ACS_HLINE, MAXX-2)
