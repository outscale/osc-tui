import curses
import sys
import threading
import time

import npyscreen
import pyperclip

import main
import securityRuleInputForm
from selectableGrid import SelectableGrid
from virtualMachine import VirtualMachine


class SecurityRulesForm(npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        y, _ = self.useable_space()
        self.draw_line_at = int(y - 9)
        self.inspector = None

        def on_selection(line):
            self.inspector.set_value(line)

        y, _ = self.useable_space()
        self.add(
            SecurityRulesGrid,
            form=self,
            name="SecurityRules",
            value=0,
            additional_y_offset=2,
            additional_x_offset=2,
            max_height=int(y / 2 - 2),
            column_width=25,
            select_whole_line=True,
            on_selection=on_selection,
            scroll_exit=True,
        )
        lbl_status = self.add_widget(
            npyscreen.Textfield,
            rely=self.draw_line_at + 2,
            value="No security rule selected",
            editable=False,
        )
        delete = self.add_widget(npyscreen.ButtonPress, name="DELETE")

        def new_sr():
            securityRuleInputForm.ask(self.inspector.form)

        def new_sr_ssh():
            main.GATEWAY.CreateSecurityGroupRule(
                FromPortRange=22,
                IpProtocol="tcp",
                IpRange=main.IP + "/32",
                ToPortRange=22,
                SecurityGroupId=main.SECURITY_GROUP,
                Flow="Inbound",
            )

        new = self.add_widget(npyscreen.ButtonPress, name="NEW")
        new.whenPressed = new_sr
        new_ssh_myip = self.add_widget(
            npyscreen.ButtonPress, name="NEW SSH FROM MY IP")
        new_ssh_myip.whenPressed = new_sr_ssh
        quit = self.add_widget(npyscreen.ButtonPress, name="EXIT")

        def stop():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = stop
        quit.whenPressed = stop
        self.inspector = Inspector(self, lbl_status, delete)

    def draw_form(self,):
        _, MAXX = self.curses_pad.getmaxyx()
        super(SecurityRulesForm, self).draw_form()
        self.curses_pad.hline(self.draw_line_at, 1, curses.ACS_HLINE, MAXX - 2)


class SecurityRulesGrid(SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.col_titles = ["DIRECTION", "PROTOCOL",
                           "FROM PORT", "TO PORT", "IP"]
        self.refresh()
        self.start_updater()

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


class Inspector:
    def __init__(self, form, name_label, delete):
        self.form = form
        self.name_label = name_label
        self.delete = delete

    def set_value(self, value):
        self.dir = value[0]
        self.protocol = "-1" if value[1] == "all" else value[1]
        self.from_port = None if value[2] == "all" else value[2]
        self.to_port = None if value[3] == "all" else value[3]
        self.ip_range = value[4]

        self.name_label.value = "Selected rule: " + str(
            value[1]
            + " from: "
            + str(value[2])
            + " to: "
            + str(value[3])
            + " with ip: "
            + str(value[4])
        )

        def delete():
            if self.from_port and self.to_port:
                main.GATEWAY.DeleteSecurityGroupRule(
                    FromPortRange=self.from_port,
                    IpProtocol=self.protocol,
                    IpRange=self.ip_range,
                    ToPortRange=self.to_port,
                    SecurityGroupId=main.SECURITY_GROUP,
                    Flow=self.dir,
                )
            else:
                main.GATEWAY.DeleteSecurityGroupRule(
                    IpProtocol=self.protocol,
                    IpRange=self.ip_range,
                    SecurityGroupId=main.SECURITY_GROUP,
                    Flow=self.dir,
                )

        self.delete.whenPressed = delete
