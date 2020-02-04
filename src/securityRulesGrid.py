
import createVm
import main
import npyscreen
import popup
import pyperclip
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
                        ])
            for rule in data["OutboundRules"]:
                for ip in rule["IpRanges"]:
                    values.append(
                        [
                            "Outbound",
                            "all" if rule["IpProtocol"] == "-1" else rule["IpProtocol"],
                            rule["FromPortRange"] if "FromPortRange" in rule else "all",
                            rule["ToPortRange"] if "ToPortRange" in rule else "all",
                            ip,
                        ])
            self.values = values

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            ip = self.values[y][4]
            cell.highlight_whole_widget = True
            if main.IP in ip:
                cell.color = "GOODHL"
            else:
                cell.color = "DEFAULT"
