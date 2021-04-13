import npyscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine


class KeyPairsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Name", "Fingerprint"]

        def on_selection(line):
            popup.editKeypair(self.form, line)

        self.on_selection = on_selection

    def refresh(self, name_filter=None):
        groups = main.GATEWAY.ReadKeypairs(form=self.form)['Keypairs']
        values = list()
        for g in groups:
            values.append([g['KeypairName'], g['KeypairFingerprint']])
        self.values = values
