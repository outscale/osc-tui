from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid


class KeyPairsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Name", "Fingerprint"]

        def on_selection(line):
            popup.editKeypair(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadKeypairs(form=self.form)
        if groups is None:
            return None
        return groups['Keypairs']

    def refresh(self, name_filter=None):
        groups = main.do_search(self.data.copy(), ['KeypairName', 'KeypairFingerprint'])
        values = list()
        for g in groups:
            values.append([g['KeypairName'], g['KeypairFingerprint']])
        self.values = values
