import npyscreen
import pyperclip
import time

import createVm
import main
import popup
import selectableGrid
import virtualMachine


class ImageGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Name", "Id", "Description", "Type", "Owner"]

        def on_selection(line):
            popup.editImage(self.form, line)

        self.on_selection = on_selection

    def refresh(self, name_filter=None):
        filter = {'Filters' : {'ImageNames' : [name_filter]}} if name_filter is not None else {}
        groups = main.GATEWAY.ReadImages(**filter)['Images']
        values = list()
        for g in groups:
            values.append([g['ImageName'], g['ImageId'], g['Description'],
                           g['ImageType'], g['AccountAlias'] if 'AccountAlias' in g else "Me"])
        self.values = values
