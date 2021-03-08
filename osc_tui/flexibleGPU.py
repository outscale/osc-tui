import npyscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine

class Grid(selectableGrid.SelectableGrid):
    def __init__(self, screen,  *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "Generation", "Model Name", "State"]

    def refresh(self):
        groups = main.GATEWAY.ReadFlexibleGpus(form=self.form)['FlexibleGpus']
        values = list()
        for g in groups:
            values.append([g['FlexibleGpuId'], g['Generation'],
                           g['ModelName'], g["State"]])
        self.values = values
