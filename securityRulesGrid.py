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
        t = updater(self)
        main.add_thread(t)
        t.start()

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

class updater(threading.Thread):
    def __init__(self, grid):
        threading.Thread.__init__(self)
        self.grid = grid
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
                self.grid.refresh()
                if self.running:
                    self.grid.display()
                self.timeSinceLastRefresh = 0
            time.sleep(1)
