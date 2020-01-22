import curses
import threading
import time

import npyscreen
import pyperclip

import createVm
import instancesGrid
import main
import securityGroupsGrid
import selectableGrid
import virtualMachine

MODE = "INSTANCES"
SELECTED_BUTTON = 0
CURRENT_GRID_CLASS = instancesGrid.InstancesGrid


class mainMenu(npyscreen.MultiLineAction):
    def __init__(self, screen, vmform=None, draw_line_at=6, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.vmform = vmform
        self.cursor_line = SELECTED_BUTTON
        self.scroll_exit = True
        self.draw_line_at = draw_line_at

    def actionHighlighted(self, act_on_this, key_press):
        if key_press == 10:

            if self.vmform:
                global MODE
                if MODE == 'INSTANCES':
                    if act_on_this == "CREATE NEW":
                        self.vmform.parentApp.addForm("CREATE_VM",
                                                      createVm.CreateVm,
                                                      name="osc-cli-curses")
                        self.vmform.parentApp.switchForm("CREATE_VM")
                        return
                elif MODE == 'SECURITY':
                    if act_on_this == "CREATE NEW":
                        npyscreen.notify("Not imlemented yet")
                        return
                if act_on_this == "EXIT":
                    main.kill_threads()
                    self.vmform.parentApp.switchForm("MAIN")
                    return
                if act_on_this == "REFRESH":
                    if hasattr(self.vmform, 'current_grid'):
                        self.vmform.current_grid.refresh()
                        self.vmform.current_grid.display()
                    return
                MODE = act_on_this
                global SELECTED_BUTTON
                SELECTED_BUTTON = self.cursor_line
                self.vmform.reload()

    def set_up_handlers(self):
        super().set_up_handlers()
        self.add_handlers({curses.KEY_RIGHT: self.h_exit_down})
        self.add_handlers({curses.KEY_LEFT: self.h_exit_up})

    def h_cursor_line_up(self, input):
        super().h_cursor_line_up(input)
        if(self.draw_line_at == self.cursor_line):
            super().h_cursor_line_up(input)
        if(self.draw_line_at == self.cursor_line):
            super().h_cursor_line_down(input)

    def h_cursor_line_down(self, input):
        super().h_cursor_line_down(input)
        if(self.draw_line_at == self.cursor_line):
            super().h_cursor_line_down(input)
        if(self.draw_line_at == self.cursor_line):
            super().h_cursor_line_up(input)


class MainForm(npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        def build_line(size):
            out = ''
            for i in range(0, size):
                out = out + '─'
            return out
        menu_desc = (
            "INSTANCES SECURITY VOLUMES SNAPSHOT REFRESH EXIT " + build_line(15)).split()
        global CURRENT_GRID_CLASS
        y, _ = self.useable_space()
        self.rowOffset = 16
        if MODE == "INSTANCES":
            CURRENT_GRID_CLASS = instancesGrid.InstancesGrid
            menu_desc.append('CREATE NEW')
        elif MODE == "SECURITY":
            CURRENT_GRID_CLASS = securityGroupsGrid.SecurityGroupsGrid
            menu_desc.append('CREATE NEW')
        elif MODE == "SECURITY-VM":
            menu_desc.append('ADD SEC-GROUP')
        self.add_widget(
            mainMenu,
            vmform=self,
            relx=1,
            max_width=14,
            max_height=10,
            values=menu_desc,
        )

        y, _ = self.useable_space()

        self.current_grid = self.add(
            CURRENT_GRID_CLASS,
            form=self,
            name="Instances",
            value=0,
            additional_y_offset=2,
            additional_x_offset=2,
            max_height=int(y / 2 - 2),
            select_whole_line=True,
            scroll_exit=True,
            relx=17,
            rely=2,
        )

    def on_screen(self):
        super().on_screen()

    def draw_form(self, ):
        _, MAXX = self.curses_pad.getmaxyx()
        super().draw_form()
        MAXX, _ = self.curses_pad.getmaxyx()
        self.curses_pad.vline(1, 15, curses.ACS_VLINE, MAXX - 2)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("Cockpit", MainForm, name="osc-cli-curses")
        self.parentApp.switchForm("Cockpit")
