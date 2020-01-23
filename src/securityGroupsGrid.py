
import npyscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine


class SecurityGroupsGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.col_titles = ["ID", "Name"]

        def on_selection(line):
            popup.editSecurityGroup(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        groups = main.GATEWAY.ReadSecurityGroups()["SecurityGroups"]
        values = list()
        for g in groups:
            values.append([g["SecurityGroupId"], g["SecurityGroupName"]])
        self.values = values


class SecurityGroupsGridForOneInstance(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.col_titles = ["ID", "Name"]
        groups = main.VM["SecurityGroups"]
        values = list()
        for g in groups:
            values.append([g["SecurityGroupId"], g["SecurityGroupName"]])
        self.values = values

        def on_selection(line):
            popup.manageSecurityGroup(self.form, line)

        self.on_selection = on_selection

    def refresh(self):
        id = main.VM["VmId"]
        data = main.GATEWAY.ReadVms()["Vms"]
        main.VMs = dict()
        for vm in data:
            main.VMs.update({vm["VmId"]: vm})
        main.VM = main.VMs[id]
        groups = main.VM["SecurityGroups"]
        values = list()
        for g in groups:
            values.append([g["SecurityGroupId"], g["SecurityGroupName"]])
        self.values = values
