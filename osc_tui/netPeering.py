from osc_tui import main
from osc_tui import selectableGrid

class Grid(selectableGrid.SelectableGrid):
    def __init__(self, screen,  *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "AccepterNet", "State"]

    def refresh_call(self, name_filter=None):
        return main.GATEWAY.ReadNetPeerings(form=self.form)['NetPeerings']

    def refresh(self):
        groups = main.do_search(self.data.copy(), ['NetPeeringId'], state_msg=True, accepted_net=True)

        values = list()
        for g in groups:
            AccepterNet = g["AccepterNet"]
            AccepterNetId = AccepterNet["NetId"] if AccepterNet else "Not Accepted"
            values.append([g['NetPeeringId'], AccepterNetId, g['State']['Message']])
        self.values = values
