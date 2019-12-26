import curses
import time
import threading

import npyscreen

import main
import virtualMachine
import selectableGrid
import securityRulesForm
import inputForm


class SecurityForm(npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        y, _ = self.useable_space()
        self.draw_line_at = int(y - 9)
        self.inspector = None

        def on_selection(line):
            main.SECURITY_GROUP = line[0]
            self.inspector.set_value(line)

        y, _ = self.useable_space()
        self.add(
            SecurityGrid,
            name="Security",
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
            value="No security group selected",
            editable=False,
        )
        edit = self.add_widget(npyscreen.ButtonPress, name="EDIT")
        new = self.add_widget(npyscreen.ButtonPress, name="ADD NEW")
        delete = self.add_widget(npyscreen.ButtonPress, name="DELETE")
        quit = self.add_widget(npyscreen.ButtonPress, name="EXIT")

        def stop():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = stop
        quit.whenPressed = stop
        self.inspector = Inspector(self, lbl_status, edit, new)

    def draw_form(self,):
        _, MAXX = self.curses_pad.getmaxyx()
        super(SecurityForm, self).draw_form()
        self.curses_pad.hline(self.draw_line_at, 1, curses.ACS_HLINE, MAXX - 2)


class SecurityGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.vms = self.next_vms
        self.col_titles = ["SECURITY GROUPS ID", "SECURITY GROUPS NAME"]

        def build_values():
            groups = main.VM["SecurityGroups"]
            values = list()
            for g in groups:
                values.append([g["SecurityGroupId"], g["SecurityGroupName"]])
            return values

        self.values = build_values()
        # Currently real time refresh is disable for this form.
        # self.values = [main.VM['SecurityGroups']['SecurityGroupId'], main.VM['SecurityGroups']['SecurityGroupName']]
        # t = updater(self)
        # main.add_thread(t)
        # t.start()

    def refresh(self):
        if main.GATEWAY:
            self.refreshing = True
            data = main.GATEWAY.ReadVms()["Vms"]
            self.next_vms = list()
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "running":
                    self.next_vms.append(_vm)
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "pending":
                    self.next_vms.append(_vm)
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "stopping":
                    self.next_vms.append(_vm)
            for vm in data:
                _vm = virtualMachine.VirtualMachine(vm)
                if _vm.status == "stopped":
                    self.next_vms.append(_vm)
            self.refreshing = False

    def summarise(self):
        summary = list()
        for vm in self.vms:
            summary.append(vm.summarise())
        return virtualMachine.summary_titles(), summary

    def updateContent(self, *args, **keywords):
        self.col_titles = ["SECURITY GROUPS"]
        self.values = [main.VM["SecurityGroups"]]


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
                self.vmGrid.on_selection(self.vmGrid.values[self.vmGrid.selected_row])
            time.sleep(1)


class Inspector:
    def __init__(self, form, name_label, edit, new):
        self.form = form
        self.name_label = name_label
        self.edit = edit
        self.new = new

    def set_value(self, value):
        self.name_label.value = "Selected group: " + value[1]

        def edit():
            main.kill_threads()
            self.form.parentApp.addForm(
                "SecurityRules",
                securityRulesForm.SecurityRulesForm,
                name="osc-cli-curses",
            )
            self.form.parentApp.switchForm("SecurityRules")

        def new():
            def create_sg(name):
                pass

            inputForm.ask(
                self.form, "Enter the new security group's name:", "", create_sg
            )

        self.edit.whenPressed = edit
        self.new.whenPressed = new
