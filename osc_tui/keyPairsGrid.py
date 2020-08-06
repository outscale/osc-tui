import npyscreen
import pyperclip

from osc_tui import createVm
from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid
from osc_tui import virtualMachine


class KeyPairsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Name", "Fingerprint"]

        def on_selection(line):
            popup.editKeypair(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        groups = main.GATEWAY.ReadKeypairs(form=self.form)['Keypairs']
        values = list()
        for g in groups:
            values.append([g['KeypairName'], g['KeypairFingerprint']])
        self.values = values
