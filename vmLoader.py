from virtualMachine import *
from vmGrid import VmGrid

def add_browser(form, on_selection):
    y, x = form.useable_space()
    return form.add(VmGrid, name = 'Instances',value = 0,
            additional_y_offset = 2, additional_x_offset = 2,# name = 'Instances',
            max_height=int(y/2-2), column_width = 15, select_whole_line = True,
            on_selection = on_selection, scroll_exit=True)