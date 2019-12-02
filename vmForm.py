import curses

import npyscreen

import main
import vmGrid
import vmInspector


class VmForm(npyscreen. FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        y, _ = self.useable_space()
        self.draw_line_at = int(y/2)
        a = None

        def on_selection(line):
            main.VM = main.VMs[line[2]]
            a.set_value(line)
        self.vmGrid = vmGrid.add_vm_browser(self, on_selection)
        a = vmInspector.add_vm_inspector(self)

    def draw_form(self,):
        _, MAXX = self.curses_pad.getmaxyx()
        super(VmForm, self).draw_form()
        self.curses_pad.hline(self.draw_line_at, 1, curses.ACS_HLINE, MAXX-2)

    def on_screen(self):
        super().on_screen()
        if not self.vmGrid.updater.isAlive():
            self.vmGrid.start_updater()
