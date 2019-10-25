import npyscreen
from osc_sdk_python import Gateway
from virtualMachine import *
import random
import vmLoader
from vmInspector import *

class CockpitForm(npyscreen.SplitForm):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
    def create(self):
        y, x = self.useable_space()
        self.draw_line_at = int(y/2)
        a = None
        def on_selection(line):
            a.set_value(line)
        vmLoader.add_browser(self, on_selection)
        a = add_inspector(self)