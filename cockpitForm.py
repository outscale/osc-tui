import vmGrid
import npyscreen
import vmInspector

class CockpitForm(npyscreen.SplitForm):
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
        