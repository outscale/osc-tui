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

MODE = "INSTANCES"
SELECTED_BUTTON = 0


class mainMenu(npyscreen.MultiLineAction):
    def __init__(self, screen, vmform=None, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.vmform = vmform
        self.cursor_line = SELECTED_BUTTON

    def actionHighlighted(self, act_on_this, key_press):
        if key_press == 10:
            # npyscreen.notify_confirm(act_on_this)
            if self.vmform:
                global MODE
                MODE = act_on_this
                global SELECTED_BUTTON
                SELECTED_BUTTON = self.cursor_line
                self.vmform.reload()
    def set_up_handlers(self):
        super().set_up_handlers()
        self.add_handlers({curses.KEY_RIGHT:   self.h_exit_down})


class VmForm(npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        y, _ = self.useable_space()
        self.draw_line_at = int(y / 2)
        self.rowOffset = 16

        self.add_widget(
            mainMenu,
            vmform=self,
            relx=1,
            max_width=13,
            max_height=10,
            values="INSTANCES SECURITY VOLUMES SNAPSHOT".split(),
        )

        if MODE == "INSTANCES":
            y, _ = self.useable_space()
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
                relx=17,
                rely=2,
            )
            y, _ = self.useable_space()
            lbl_status = self.add_widget(
                npyscreen.Textfield,
                rely=int(y / 2 + 1),
                value="No instance selected",
                editable=False,
                relx=self.rowOffset,
            )

            # Buttons about VMs
            btn_run_stop = self.add_widget(
                npyscreen.ButtonPress, name="RUN", relx=self.rowOffset
            )
            btn_restart = self.add_widget(
                npyscreen.ButtonPress, name="RESTART", relx=self.rowOffset
            )
            btn_force_stop = self.add_widget(
                npyscreen.ButtonPress, name="FORCE STOP", relx=self.rowOffset
            )
            btn_terminate = self.add_widget(
                npyscreen.ButtonPress, name="TERMINATE", relx=self.rowOffset
            )
            btn_copy_ip = self.add_widget(
                npyscreen.ButtonPress, name="COPY IP", relx=self.rowOffset
            )
            btn_create_vm = self.add_widget(
                npyscreen.ButtonPress, name="CREATE VM", relx=self.rowOffset
            )
            btn_security = self.add_widget(
                npyscreen.ButtonPress, name="SECURITY", relx=self.rowOffset
            )
            btn_quit = self.add_widget(
                npyscreen.ButtonPress, name="EXIT", relx=self.rowOffset
            )

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

    def on_screen(self):
        super().on_screen()
        # if not self.vm_grid.updater.isAlive():
        #   self.vm_grid.start_updater()

    def draw_form(self,):
        _, MAXX = self.curses_pad.getmaxyx()
        super().draw_form()
        if self.draw_line_at:
            self.curses_pad.hline(self.draw_line_at, 14, curses.ACS_HLINE, MAXX - 15)
        MAXX, _ = self.curses_pad.getmaxyx()
        self.curses_pad.vline(1, 14, curses.ACS_VLINE, MAXX - 2)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("Cockpit", VmForm, name="osc-cli-curses")
        self.parentApp.switchForm("Cockpit")


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
            elif status == "terminated" or status == "shutting-down":
                cell.color = "DANGER"


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
        self.status = vm[0]
        self.id = vm[2]
        self.vm = vm
        self.name = vm[1]
        self.name_label.value = "Instance selected: " + self.name
        self.force_stop.hidden = (
            True if self.status == "stopped" or self.status == "terminated" else False
        )
        self.restart.hidden = False if self.status == "running" else True
        self.sg.hidden = True if self.status == "terminated" else False
        self.copy_ip.hidden = (
            True if self.status == "terminated" or self.status == "stopped" else False
        )
        self.terminate.hidden = True if self.status == "terminated" else False
        if self.status == "running" or self.status == "stopped":
            self.run_stop.name = "RUN" if vm[0] == "stopped" else "STOP"
            self.run_stop.hidden = False
        else:
            self.run_stop.hidden = True
        if self.status == "terminated":
            self.sg.hidden = True
        else:
            self.sg.hidden = False
        self.name_label.update()
        self.run_stop.update()
        # Operations availables:

        def copy_ip():
            pyperclip.copy(vm[5])

        def start_vm():
            main.GATEWAY.StartVms(VmIds=[vm[2]])

        def terminate_vm():
            main.kill_threads()
            if npyscreen.notify_ok_cancel(
                "Do you really want to terminate this vm:\nName: "
                + self.name
                + "\nID: "
                + self.id,
                "VM Termination",
            ):
                main.GATEWAY.DeleteVms(VmIds=[vm[2]])
            self.form.vm_grid.start_updater()

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
