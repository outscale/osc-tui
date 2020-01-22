import curses
import threading
import time

import npyscreen
import pyperclip

import createVm
import main
import popup
import selectableGrid
import virtualMachine


class SecurityRulesGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.col_titles = ["DIRECTION", "PROTOCOL",
                           "FROM PORT", "TO PORT", "IP"]
        self.refresh()
        self.start_updater()
        def on_selection(line):
            popup.editSecurityGroupRule(self.form, line)
        self.on_selection = on_selection

    def refresh(self):
        if main.GATEWAY:
            self.refreshing = True
            data = main.GATEWAY.ReadSecurityGroups(
                Filters={"SecurityGroupIds": [main.SECURITY_GROUP]}
            )["SecurityGroups"][0]
            values = list()
            for rule in data["InboundRules"]:
                for ip in rule["IpRanges"]:
                    values.append(
                        [
                            "Inbound",
                            "all" if rule["IpProtocol"] == "-1" else rule["IpProtocol"],
                            rule["FromPortRange"] if "FromPortRange" in rule else "all",
                            rule["ToPortRange"] if "ToPortRange" in rule else "all",
                            ip,
                        ]
                    )
            for rule in data["OutboundRules"]:
                for ip in rule["IpRanges"]:
                    values.append(
                        [
                            "Outbound",
                            "all" if rule["IpProtocol"] == "-1" else rule["IpProtocol"],
                            rule["FromPortRange"] if "FromPortRange" in rule else "all",
                            rule["ToPortRange"] if "ToPortRange" in rule else "all",
                            ip,
                        ]
                    )
            self.values = values

