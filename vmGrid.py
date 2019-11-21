import threading
import time

import main
from selectableGrid import SelectableGrid
from virtualMachine import *


def add_vm_browser(form, on_selection):
    y, _ = form.useable_space()
    return form.add(VmGrid, name='Instances', value=0,
                    additional_y_offset=2, additional_x_offset=2,  # name = 'Instances',
                    max_height=int(y/2-2), column_width=17, select_whole_line=True,
                    on_selection=on_selection, scroll_exit=True)


class VmGrid(SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.vms = self.next_vms
        self.col_titles, self.values = self.summarise()
        t = updater(self)
        main.add_thread(t)
        t.start()

    def refresh(self):
        if main.GATEWAY:
            self.refreshing = True
            data = main.GATEWAY.ReadVms()["Vms"]
            self.next_vms = list()
            main.VMs = dict()
            for vm in data:
                _vm = VirtualMachine(vm)
                if _vm.status == 'running':
                    self.next_vms.append(_vm)
            for vm in data:
                _vm = VirtualMachine(vm)
                if _vm.status == 'pending':
                    self.next_vms.append(_vm)
            for vm in data:
                _vm = VirtualMachine(vm)
                if _vm.status == 'stopping':
                    self.next_vms.append(_vm)
            for vm in data:
                _vm = VirtualMachine(vm)
                if _vm.status == 'stopped':
                    self.next_vms.append(_vm)
            for vm in data:
                main.VMs.update({vm['VmId'] : vm})
            self.refreshing = False

    def summarise(self):
        summary = list()
        for vm in self.vms:
            summary.append(vm.summarise())
        return summary_titles(), summary

    def updateContent(self, *args, **keywords):
        self.col_titles, self.values = self.summarise()


class updater(threading.Thread):
    def __init__(self, vmGrid):
        threading.Thread.__init__(self)
        self.vmGrid = vmGrid
        self.t1 = int(round(time.time() * 1000))
        self.t2 = int(round(time.time() * 1000))
        self.timeSinceLastRefresh = 0
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        while self.running == True:
            self.t2 = int(round(time.time() * 1000))
            dt = self.t2 - self.t1
            self.timeSinceLastRefresh += dt
            if self.timeSinceLastRefresh > 2000:
                self.vmGrid.refresh()
                self.vmGrid.vms = self.vmGrid.next_vms
                self.vmGrid.updateContent()
                if self.running:
                    self.vmGrid.display()
                self.timeSinceLastRefresh = 0
                self.vmGrid.on_selection(
                    self.vmGrid.values[self.vmGrid.selected_row])
            time.sleep(0.5)
