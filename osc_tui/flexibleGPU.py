from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class Grid(selectableGrid.SelectableGrid):
    def __init__(self, screen,  *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "Generation", "Model Name", "State"]
        def on_selection(line):
            popup.editFlexibleGpu(self.form, line)
        self.on_selection = on_selection


    def refresh_call(self, name_filter=None):
        ret =  main.GATEWAY.ReadFlexibleGpus(form=self.form)
        if ret:
            return ret['FlexibleGpus']
        return None

    def refresh(self):
        groups = main.do_search(self.data.copy(), ['FlexibleGpuId', 'Generation', 'ModelName', 'State'])
        values = list()
        for g in groups:
            values.append([g['FlexibleGpuId'], g['Generation'],
                           g['ModelName'], g["State"]])
        self.values = values
