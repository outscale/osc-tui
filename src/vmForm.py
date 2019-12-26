import curses
import threading
import time

import npyscreen
import pyperclip

import main
import securityForm
import selectableGrid
import virtualMachine
import createVm


class VmForm(npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        y, _ = self.useable_space()
        self.draw_line_at = int(y / 2)
        self.inspector = None

        def cb_on_selection(line):
            main.VM = main.VMs[line[2]]
            self.inspector.set_value(line)

        y, _ = self.useable_space()
        self.vm_grid = self.add(
            VmGrid,
            name="Instances",
            value=0,
            additional_y_offset=2,
            additional_x_offset=2,
            max_height=int(y / 2 - 2),
            column_width=17,
            select_whole_line=True,
            on_selection=cb_on_selection,
            scroll_exit=True,
        )
        y, _ = self.useable_space()
        lbl_status = self.add_widget(
            npyscreen.Textfield,
            rely=int(y / 2 + 1),
            value="No instance selected",
            editable=False,
        )
        btn_run_stop = self.add_widget(npyscreen.ButtonPress, name="RUN")
        btn_restart = self.add_widget(npyscreen.ButtonPress, name="RESTART")
        btn_force_stop = self.add_widget(npyscreen.ButtonPress, name="FORCE STOP")
        btn_terminate = self.add_widget(npyscreen.ButtonPress, name="TERMINATE")
        btn_copy_ip = self.add_widget(npyscreen.ButtonPress, name="COPY IP")
        btn_create_vm = self.add_widget(npyscreen.ButtonPress, name="CREATE VM")
        btn_security = self.add_widget(npyscreen.ButtonPress, name="SECURITY")
        btn_quit = self.add_widget(npyscreen.ButtonPress, name="EXIT")

        def cb_stop():
            main.kill_threads()
            self.parentApp.switchForm("MAIN")

        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = cb_stop
        btn_quit.whenPressed = cb_stop

        def cb_create_vm():
            main.kill_threads()
            self.parentApp.addForm(
                "CREATE_VM", createVm.CreateVm, name="osc-cli-curses"
            )
            self.parentApp.switchForm("CREATE_VM")

        btn_create_vm.whenPressed = cb_create_vm
        self.inspector = Inspector(
            self,
            lbl_status,
            btn_run_stop,
            btn_restart,
            btn_force_stop,
            btn_copy_ip,
            btn_security,
            btn_terminate,
        )

    def draw_form(self,):
        _, MAXX = self.curses_pad.getmaxyx()
        super(VmForm, self).draw_form()
        self.curses_pad.hline(self.draw_line_at, 1, curses.ACS_HLINE, MAXX - 2)

    def on_screen(self):
        super().on_screen()
        if not self.vm_grid.updater.isAlive():
            self.vm_grid.start_updater()


class VmGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.refresh()
        self.start_updater()

    def refresh(self):
        if main.GATEWAY:
            self.refreshing = True
            data = main.GATEWAY.ReadVms()["Vms"]
            self.vms = list()
            main.VMs = dict()
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


class Inspector:
    def __init__(
        self, form, name_label, run_stop, restart, force_stop, cp_ip, sg, terminate
    ):
        self.form = form
        self.copy_ip = cp_ip
        self.name_label = name_label
        self.run_stop = run_stop
        self.force_stop = force_stop
        self.restart = restart
        self.sg = sg
        self.terminate = terminate

    def set_value(self, vm):
        self.vm = vm
        self.name = vm[1]
        self.name_label.value = "Instance selected: " + self.name
        self.run_stop.name = "RUN" if vm[0] == "stopped" else "STOP"
        self.name_label.update()
        self.run_stop.update()
        # Operations availables:

        def copy_ip():
            pyperclip.copy(vm[5])

        def start_vm():
            main.GATEWAY.StartVms(VmIds=[vm[2]])

        def terminate_vm():
            main.GATEWAY.DeleteVms(VmIds=[vm[2]])

        def stop_vm():
            main.GATEWAY.StopVms(VmIds=[vm[2]])

        def force_stop_vm():
            main.GATEWAY.StopVms(ForceStop=True, VmIds=[vm[2]])

        def restart_vm():
            main.GATEWAY.RebootVms(VmIds=[vm[2]])

        def security():
            main.kill_threads()
            self.form.parentApp.addForm(
                "Security", securityForm.SecurityForm, name="osc-cli-curses"
            )
            self.form.parentApp.switchForm("Security")

        self.copy_ip.whenPressed = copy_ip
        self.run_stop.whenPressed = start_vm if vm[0] == "stopped" else stop_vm
        self.force_stop.whenPressed = force_stop_vm
        self.restart.whenPressed = restart_vm
        self.sg.whenPressed = security
        self.terminate.whenPressed = terminate_vm
