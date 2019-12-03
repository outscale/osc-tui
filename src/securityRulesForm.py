import curses
import sys
import threading
import time

import npyscreen
import pyperclip

import main
import securityForm
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
        new_ssh_myip = self.add_widget(npyscreen.ButtonPress, name="NEW SSH FROM MY IP")
        new_ssh_myip.whenPressed = new_sr_ssh
        quit = self.add_widget(npyscreen.ButtonPress, name="EXIT")

        def stop():
            main.kill_threads()
            self.parentApp.switchForm("Security")

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
        self.col_titles = ["PROTOCOL", "FROM PORT", "TO PORT", "IP"]
        self.refresh()
        self.start_updater()

    def refresh(self):
        if main.GATEWAY:
            self.refreshing = True
            data = main.GATEWAY.ReadSecurityGroups(
                Filters={"SecurityGroupIds": [main.SECURITY_GROUP]}
            )["SecurityGroups"][0]["InboundRules"]
            values = list()
            for rule in data:
                for ip in rule["IpRanges"]:
                    values.append(
                        [
                            rule["IpProtocol"],
                            rule["FromPortRange"],
                            rule["ToPortRange"],
                            ip,
                        ]
                    )
            self.values = values

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            ip = self.values[y][3]
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
        self.protocol = value[0]
        self.from_port = value[1]
        self.to_port = value[2]
        self.ip_range = value[3]

        self.name_label.value = "Selected rule: " + str(
            value[0]
            + " from: "
            + str(value[1])
            + " to: "
            + str(value[2])
            + " with ip: "
            + str(value[3])
        )

        def delete():
            main.GATEWAY.DeleteSecurityGroupRule(
                FromPortRange=self.from_port,
                IpProtocol=self.protocol,
                IpRange=self.ip_range,
                ToPortRange=self.to_port,
                SecurityGroupId=main.SECURITY_GROUP,
                Flow="Inbound",
            )

        self.delete.whenPressed = delete
