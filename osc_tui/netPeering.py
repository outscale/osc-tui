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
        self.col_titles = ["Id", "AccepterNet", "State"]

    def refresh(self):
        groups = main.GATEWAY.ReadNetPeerings(form=self.form)['NetPeerings']
        values = list()
        for g in groups:
            AccepterNet = g["AccepterNet"]
            AccepterNetId = AccepterNet["NetId"] if AccepterNet else "Not Accepted"
            values.append([g['NetPeeringId'], AccepterNetId, g['State']['Message']])
        self.values = values
