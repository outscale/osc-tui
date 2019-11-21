import threading
import time

import main
from selectableGrid import SelectableGrid
from virtualMachine import *


def add_security_rules_grid(form, on_selection):
    y, _ = form.useable_space()
    return form.add(SecurityRulesGrid, name='SecurityRules', value=0,
                    additional_y_offset=2, additional_x_offset=2,  # name = 'Instances',
                    max_height=int(y/2-2),
                    column_width=25,
                    select_whole_line=True,
                    on_selection=on_selection, scroll_exit=True)


class SecurityRulesGrid(SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.col_titles = ['PROTOCOL', 'FROM PORT', 'TO PORT', 'IP']
        self.refresh()
        #self.values = [main.VM['SecurityGroups']['SecurityGroupId'], main.VM['SecurityGroups']['SecurityGroupName']]
        #t = updater(self)
        # main.add_thread(t)
        # t.start()

    def refresh(self):
        if main.GATEWAY:
            self.refreshing = True
            data = main.GATEWAY.ReadSecurityGroups(Filters={
                "SecurityGroupIds": [
                    "sg-ceb6c7a7"
                ]})['SecurityGroups'][0]['InboundRules']
            values = list()
            for rule in data:
                for ip in rule['IpRanges']:
                    values.append([rule['IpProtocol'], rule['FromPortRange'], rule['ToPortRange'], ip])
            self.values = values

    def summarise(self):
        summary = list()
        for vm in self.vms:
            summary.append(vm.summarise())
        return summary_titles(), summary

    def updateContent(self, *args, **keywords):
        self.col_titles = ['SECURITY GROUPS']
        self.values = [main.VM['SecurityGroups']]


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
            time.sleep(1)
