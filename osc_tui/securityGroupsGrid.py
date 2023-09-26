from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid


class SecurityGroupsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "Name"]

        def on_selection(line):
            popup.editSecurityGroup(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        return main.GATEWAY.ReadSecurityGroups(form=self.form)["SecurityGroups"]

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["SecurityGroupId", "SecurityGroupName"])
        values = list()
        for g in groups:
            values.append([g["SecurityGroupId"], g["SecurityGroupName"]])
        self.values = values


class SecurityGroupsGridForOneInstance(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "Name"]
        groups = main.VM["SecurityGroups"]
        values = list()
        for g in groups:
            values.append([g["SecurityGroupId"], g["SecurityGroupName"]])
        self.values = values

        def on_selection(line):
            popup.manageSecurityGroup(self.form, line)

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        id = main.VM["VmId"]
        data = main.GATEWAY.ReadVms()["Vms"]
        main.VMs = dict()
        for vm in data:
            main.VMs.update({vm["VmId"]: vm})
        main.VM = main.VMs[id]
        groups = main.VM["SecurityGroups"]
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["SecurityGroupId", "SecurityGroupName"])
        values = list()
        for g in groups:
            values.append([g["SecurityGroupId"], g["SecurityGroupName"]])
        self.values = values
