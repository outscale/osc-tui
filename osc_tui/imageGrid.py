import npyscreen
import pyperclip

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

    def refresh(self):
        groups = main.GATEWAY.ReadImages(form=self.form)['Images']
        values = list()
        for g in groups:
            values.append([g['ImageName'], g['ImageId'], g['Description'],
                           g['ImageType'], g['AccountAlias'] if 'AccountAlias' in g else "Me"])
        self.values = values
