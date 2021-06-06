import curses

import npyscreen
import pyperclip

import createKeyPair
import createSnapshot
import createVm
import createVolume
import createLoadbalancer
import createVpcs
import createNetAccessPoint
import imageGrid
import instancesGrid
import keyPairsGrid
import vpcsGrid
import main
import netAccesssPoint
import netPeering
import flexibleGPU
import popup
import securityGroupsGrid
import securityRulesGrid
import selectableGrid
import snapshotGrid
import loadbalancerGrid
import virtualMachine
import volumesGrid

MODE = "INSTANCES"
SELECTED_BUTTON = 0
CURRENT_GRID_CLASS = instancesGrid.InstancesGrid


class mainMenu(npyscreen.MultiLineAction):
    def __init__(self, screen, form=None, draw_line_at=13, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.form = form
        self.cursor_line = SELECTED_BUTTON
        self.scroll_exit = True
        self.draw_line_at = draw_line_at

    def actionHighlighted(self, act_on_this, key_press):
        if key_press == 10:

            if self.form:
                global MODE
                if MODE == 'INSTANCES-LBU':
                    if act_on_this == "CREATE NEW":
                        npyscreen.notify_confirm("Not implemented yet :/")
                        return
                elif MODE == 'INSTANCES':
                    if act_on_this == "CREATE NEW":
                        self.form.parentApp.addForm("CREATE_VM",
                                                    createVm.CreateVm,
                                                    name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_VM")
                        return
                elif MODE == 'SECURITY':
                    if act_on_this == "CREATE NEW":
                        popup.newSecurityGroup(self.form)
                        return
                elif MODE == 'SECURITY-VM':
                    if act_on_this == "ADD SEC-GROUP":
                        popup.addSecurityGroupToVm(self.form)
                        return
                elif MODE == 'SECURITY-RULES':
                    if act_on_this == "CREATE NEW":
                        popup.newSecurityGroupRule(self.form)
                        return
                    elif act_on_this == 'ADD SSH MY IP':
                        main.GATEWAY.CreateSecurityGroupRule(
                            form=self.form,
                            FromPortRange=22,
                            IpProtocol="tcp",
                            IpRange=main.IP + "/32",
                            ToPortRange=22, SecurityGroupId=main.SECURITY_GROUP,
                            Flow="Inbound",
                        )
                        self.form.current_grid.h_refresh(None)
                        self.form.current_grid.display()
                        return
                elif MODE == 'VOLUMES':
                    if act_on_this == 'CREATE NEW':
                        self.form.parentApp.addForm(
                            "CREATE_VOLUME", createVolume.CreateVolume, name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_VOLUME")
                        return
                elif MODE == 'SNAPSHOT':
                    if act_on_this == 'CREATE NEW':
                        self.form.parentApp.addForm(
                            "CREATE_SNAPSHOT", createSnapshot.CreateSnapshot, name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_SNAPSHOT")
                        return
                elif MODE == 'KEYPAIRS':
                    if act_on_this == 'CREATE NEW':
                        self.form.parentApp.addForm(
                            "CREATE_KEYPAIR", createKeyPair.CreateKeyPair, name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_KEYPAIR")
                        return
                elif MODE == 'LBUs':
                    if act_on_this == 'CREATE NEW':
                        self.form.parentApp.addForm(
                            "CREATE_LOADBALANCER",
                            createLoadbalancer.CreateLoadbalancer,
                            name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_LOADBALANCER")
                        return
                elif MODE == 'VPCs(nets)':
                    if act_on_this == 'CREATE NEW':
                        self.form.parentApp.addForm(
                            "CREATE_VPCs",
                            createVpcs.createVpcs,
                            name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_VPCs")
                        return
                elif MODE == 'SUBNET':
                    if act_on_this == 'CREATE NEW':
                        self.form.parentApp.addForm(
                            "CREATE_SUBNET",
                            createVpcs.createSubnet,
                            name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_SUBNET")
                        return
                elif MODE == 'NET-ACCESS-POINT':
                    if act_on_this == 'CREATE NEW':
                        self.form.parentApp.addForm(
                            "CREATE_NET-ACCESS-POINT",
                            createNetAccessPoint.CreateNetAccessPoint,
                            name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_NET-ACCESS-POINT")
                        return
                if act_on_this == "EXIT":
                    main.kill_threads()
                    self.form.parentApp.switchForm("MAIN")
                    return
                elif act_on_this == "REFRESH":
                    if hasattr(self.form, 'current_grid'):
                        self.form.current_grid.h_refresh(None)
                        self.form.current_grid.display()
                    return
                MODE = act_on_this
                global SELECTED_BUTTON
                if act_on_this == 'INSTANCES' or act_on_this == 'SECURITY':
                    SELECTED_BUTTON = 11
                else:
                    SELECTED_BUTTON = self.cursor_line
                self.form.reload()
    
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
                out = out + '-'
            return out
        menu_desc = (
            "INSTANCES SECURITY VOLUMES SNAPSHOT KEYPAIRS IMAGES LBUs VPCs(nets) NET-ACCESS-POINT NET-PEERING GPU REFRESH EXIT " +
            build_line(15)).split()
        global CURRENT_GRID_CLASS
        y, _ = self.useable_space()
        self.rowOffset = 16
        if MODE == "INSTANCES":
            CURRENT_GRID_CLASS = instancesGrid.InstancesGrid
            menu_desc.append('CREATE NEW')
        elif MODE == "INSTANCES-LBU":
            CURRENT_GRID_CLASS = instancesGrid.InstancesGridLBU
            menu_desc.append('CREATE NEW')
        elif MODE == "SECURITY":
            CURRENT_GRID_CLASS = securityGroupsGrid.SecurityGroupsGrid
            menu_desc.append('CREATE NEW')
        elif MODE == "SECURITY-VM":
            CURRENT_GRID_CLASS = securityGroupsGrid.SecurityGroupsGridForOneInstance
            menu_desc.append('ADD SEC-GROUP')
        elif MODE == 'SECURITY-RULES':
            CURRENT_GRID_CLASS = securityRulesGrid.SecurityRulesGrid
            menu_desc.append('CREATE NEW')
            menu_desc.append('ADD SSH MY IP')
        elif MODE == 'VOLUMES':
            CURRENT_GRID_CLASS = volumesGrid.VolumeGrid
            menu_desc.append('CREATE NEW')
        elif MODE == 'VOLUMES-VM':
            CURRENT_GRID_CLASS = volumesGrid.VolumeGridForOneInstance
        elif MODE == 'SNAPSHOT':
            CURRENT_GRID_CLASS = snapshotGrid.SnapshotGrid
            menu_desc.append('CREATE NEW')
        elif MODE == 'IMAGES':
            CURRENT_GRID_CLASS = imageGrid.ImageGrid
        elif MODE == 'LBUs':
            CURRENT_GRID_CLASS = loadbalancerGrid.loadbalancerGrid
            menu_desc.append('CREATE NEW')
        elif MODE == 'VPCs(nets)':
            CURRENT_GRID_CLASS = vpcsGrid.vpcsGrid
            menu_desc.append('CREATE NEW')
        elif MODE == 'NET-ACCESS-POINT':
            CURRENT_GRID_CLASS = netAccesssPoint.Grid
            menu_desc.append('CREATE NEW')
        elif MODE == 'NET-PEERING':
            CURRENT_GRID_CLASS = netPeering.Grid
        elif MODE == 'GPU':
            CURRENT_GRID_CLASS = flexibleGPU.Grid
        elif MODE == 'SUBNET':
            CURRENT_GRID_CLASS = vpcsGrid.subnetGrid
            menu_desc.append('CREATE NEW')
        elif MODE == 'KEYPAIRS':
            CURRENT_GRID_CLASS = keyPairsGrid.KeyPairsGrid
            menu_desc.append('CREATE NEW')
        self.add_widget(
            mainMenu,
            form=self,
            relx=1,
            max_width=14,
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
            column_width=21,
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
        self.parentApp.addForm("Cockpit", MainForm, name="osc-tui")
        self.parentApp.switchForm("Cockpit")

    def quit_key(form, key_val):
        main.kill_threads()
        form.parentApp.switchForm("MAIN")
        
    def set_up_handlers(self):
        super().set_up_handlers()
        self.add_handlers({"q": self.quit_key})
        self.add_handlers({"^Q": quit})
        self.add_handlers({"h": popup.showHelp})

