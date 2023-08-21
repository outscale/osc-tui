from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid
from osc_tui import virtualMachine

#authentication.VERSION
class InstancesGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.column_width = 17

        def on_selection_cb(line):
            popup.editInstance(self.form, line)
        self.on_selection = on_selection_cb

    def refresh_call(self, name_filter=None):
        return main.readVms()


    def refresh(self):
        if main.GATEWAY:
            self.refreshing = True

            self.vms = list()
            main.VMs = dict()
            data = main.do_search(self.data.copy(), ["State", "VmId", "VmType",
                                              "PrivateIp", "PublicIp",
                                              "KeypairName"],
                                  name_as_tag=True, az=True)

            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "running":
                    self.vms.append(_vm)
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "pending":
                    self.vms.append(_vm)
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "stopping":
                    self.vms.append(_vm)
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "stopped":
                    self.vms.append(_vm)
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "shutting-down":
                    self.vms.append(_vm)
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "terminated":
                    self.vms.append(_vm)
            for vm in data:
                main.VMs.update({vm["VmId"]: vm})
            self.col_titles, self.values = self.summarise()
            self.refreshing = False

    def summarise(self):
        summary = list()
        for vm in self.vms:
            summary.append(vm.summarise())
        return virtualMachine.summary_titles(), summary

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            status = self.values[y][0]
            cell.highlight_whole_widget = True
            if status == "running":
                cell.color = "GOODHL"
            elif status == "pending":
                cell.color = "RED_BLACK"
            elif status == "stopping":
                cell.color = "RED_BLACK"
            elif status == "stopped":
                cell.color = "CURSOR"
            elif status == "terminated" or status == "shutting-down":
                cell.color = "DANGER"


class InstancesGridLBU(InstancesGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.column_width = 17

        def on_selection_cb(line):
            popup.editInstanceInLBU(self.form, line)
        self.on_selection = on_selection_cb

    def refresh(self, name_filter=None):
        main.LBUs = main.GATEWAY.ReadLoadBalancers(form=self.form)[
            'LoadBalancers']
        super().refresh()

    def summarise(self):
        summary = list()
        lbu = None
        for lbu_tmp in main.LBUs:
            if lbu_tmp['LoadBalancerName'] == main.LBU:
                lbu = lbu_tmp
                break
        for vm in self.vms:
            if vm.summarise()[2] in lbu['BackendVmIds']:
                summary.append(vm.summarise())
        return virtualMachine.summary_titles(), summary
