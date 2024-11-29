import curses
import ipaddress

import osc_npyscreen

import graphviz

import osc_sdk_python

import time

from osc_tui import createImage
from osc_tui import createKeyPair
from osc_tui import createSnapshot
from osc_tui import createVm
from osc_tui import createVolume
from osc_tui import createLoadbalancer
from osc_tui import createVpcs
from osc_tui import createNetAccessPoint
from osc_tui import imageGrid
from osc_tui import instancesGrid
from osc_tui import keyPairsGrid
from osc_tui import vpcsGrid
from osc_tui import main
from osc_tui import netAccesssPoint
from osc_tui import netPeering
from osc_tui import flexibleGPU
from osc_tui import popup
from osc_tui import securityGroupsGrid
from osc_tui import securityRulesGrid
from osc_tui import snapshotGrid
from osc_tui import loadbalancerGrid
from osc_tui import volumesGrid
from osc_tui import guiRules
from osc_tui import nicsGrid
from osc_tui import publicIps
from osc_tui import internetServices
from osc_tui import routeTables
from osc_tui import dhcpOptions
from osc_tui import natServices
from osc_tui import userGrid

from osc_diagram import osc_diagram

MODE = "Vms"
SELECTED_BUTTON = 0
CURRENT_GRID_CLASS = instancesGrid.InstancesGrid

MENU_WIDTH = 16
LINE_SEPARATOR_COL = MENU_WIDTH + 1
GRID_START_COL = MENU_WIDTH +3

def swicthToVolumeEdit(self, id, volume):
    self.parentApp.addForm("Volume-Edit",
                           volumesGrid.VolumeEdit,
                           volume=volume,
                           name="osc-tui Volume-Edit {}".format(id))
    self.parentApp.switchForm("Volume-Edit")

def swicthToVolumeLink(self, id, volume):
    self.parentApp.addForm("Volume-Link",
                           volumesGrid.VolumeLink,
                           volume=volume,
                           name="osc-tui Volume-Link {}".format(id))
    self.parentApp.switchForm("Volume-Link")


# update draw_line_at when adding a new resource
class mainMenu(osc_npyscreen.MultiLineAction):
    def __init__(self, screen, form=None, draw_line_at=20, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.form = form
        self.cursor_line = SELECTED_BUTTON
        self.scroll_exit = False
        self.draw_line_at = draw_line_at

    def actionHighlighted(self, act_on_this, key_press):
        if key_press == 10:

            global FILTER
            if self.form:
                global MODE
                if MODE == 'INSTANCES-LBU':
                    if act_on_this == "Create new":
                        osc_npyscreen.notify_confirm("Not implemented yet :/")
                        return
                elif MODE == 'Vms':
                    if act_on_this == "Create new":
                        self.form.parentApp.addForm("CREATE_VM",
                                                    createVm.CreateVm,
                                                    name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_VM")
                        return
                    if act_on_this == 'Visual Graph':
                        try:
                            osc_diagram(ak=main.GATEWAY.access_key(), sk=main.GATEWAY.secret_key(),
                                        format=["png"])
                        except graphviz.backend.ExecutableNotFound:
                            osc_npyscreen.notify_confirm("Fail to generate graph, did you install graphviz ?")
                        except osc_sdk_python.outscale_gateway.ActionNotExists:
                            osc_npyscreen.notify_confirm("osc-sdk-python is too old for this feature")
                        except Exception:
                            osc_npyscreen.notify_confirm("osc-diagram fail for an unknow reason...(the lib is very young)")
                        return

                elif MODE == 'Security':
                    if act_on_this == "Create new":
                        popup.newSecurityGroup(self.form)
                        return
                elif MODE == 'SECURITY-VM':
                    if act_on_this == "ADD SEC-GROUP":
                        popup.addSecurityGroupToVm(self.form)
                        return
                elif MODE == 'SECURITY-RULES':
                    if act_on_this == "Create new":
                        popup.newSecurityGroupRule(self.form)
                        return
                    elif act_on_this == 'Add my ssh IP':
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
                    if guiRules.RULES is not None and MODE in guiRules.RULES:
                        for name in guiRules.RULES[MODE]:
                            if act_on_this == name:
                                rule=guiRules.RULES[MODE][name]
                                ips=[]
                                if "ips" in rule:
                                    ips=rule["ips"]
                                else:
                                    ipstr=popup.readString(name="Enter IP:")
                                    ips.append(ipstr)
                                try:
                                    for ipstr in ips:
                                        ip=ipaddress.ip_network(ipstr)
                                        for p in rule["ports"]:
                                            for proto in rule["protocols"]:
                                                main.GATEWAY.CreateSecurityGroupRule(
                                                    form=self.form,
                                                    FromPortRange=p,
                                                    IpProtocol=proto,
                                                    IpRange=str(ip),
                                                    ToPortRange=p,
                                                    SecurityGroupId=main.SECURITY_GROUP,
                                                    Flow="Inbound"
                                                )
                                                self.form.current_grid.h_refresh(None)
                                                self.form.current_grid.display()
                                except ValueError:
                                    osc_npyscreen.notify_confirm("{} is not an IP :/".format(ipstr))
                                return

                elif MODE == 'Volumes':
                    if act_on_this == 'Create new':
                        self.form.parentApp.addForm(
                            "CREATE_VOLUME", createVolume.CreateVolume, name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_VOLUME")
                        return
                elif MODE == 'Snapshots':
                    if act_on_this == 'Create new':
                        self.form.parentApp.addForm(
                            "CREATE_SNAPSHOT", createSnapshot.CreateSnapshot, name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_SNAPSHOT")
                        return
                elif MODE == 'Keypairs':
                    if act_on_this == 'Create new':
                        self.form.parentApp.addForm(
                            "CREATE_KEYPAIR", createKeyPair.CreateKeyPair, name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_KEYPAIR")
                        return
                elif MODE == 'LoadBalancers':
                    if act_on_this == 'Create new':
                        self.form.parentApp.addForm(
                            "CREATE_LOADBALANCER",
                            createLoadbalancer.CreateLoadbalancer,
                            name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_LOADBALANCER")
                        return
                elif MODE == 'Nets':
                    if act_on_this == 'Create new':
                        self.form.parentApp.addForm(
                            "CREATE_VPCS",
                            createVpcs.CreateVpcs,
                            name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_VPCS")
                        return
                elif MODE == 'Images':
                    if act_on_this == 'Filter':
                        popup.addFilter(self.form)
                        return
                    if act_on_this == 'Create new':
                        self.form.parentApp.addForm(
                            "CREATE_Images",createImage.CreateImage,name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_Images")
                        return
                elif MODE == 'Subnets':
                    if act_on_this == 'Create new':
                        self.form.parentApp.addForm(
                            "CREATE_SUBNET",
                            createVpcs.CreateSubnet,
                            name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_SUBNET")
                        return
                elif MODE == 'NetAccessPoints':
                    if act_on_this == 'Create new':
                        self.form.parentApp.addForm(
                            "CREATE_NET-ACCESS-POINT",
                            createNetAccessPoint.CreateNetAccessPoint,
                            name="osc-tui")
                        self.form.parentApp.switchForm("CREATE_NET-ACCESS-POINT")
                        return
                if act_on_this == "Quit":
                    main.kill_threads()
                    self.form.parentApp.switchForm("MAIN")
                    return
                elif act_on_this == "Refresh":
                    if hasattr(self.form, 'current_grid'):
                        self.form.current_grid.h_refresh(None)
                        self.form.current_grid.display()
                    return
                MODE = act_on_this
                global SELECTED_BUTTON
                SELECTED_BUTTON = self.cursor_line
                self.form.reload()
    
    def set_up_handlers(self):
        super().set_up_handlers()
        self.add_handlers({curses.KEY_RIGHT: self.h_exit_down})
        self.add_handlers({curses.KEY_LEFT: self.h_exit_up})
        #self.add_handlers({curses.ascii.TAB: self.h_exit_up})

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


class MainForm(osc_npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        def build_line(size):
            out = ''
            for i in range(0, size):
                out = out + '‎'
            return out
        menu_desc = (
            "Vms Security Volumes Snapshots Keypairs Images LoadBalancers Nets Subnets PublicIps Nics NetAccessPoints NetPeering InternetServices NatServices RouteTables DhcpOptions GPUs Users UserGroups " + build_line(15) + " Refresh Quit").split()
        global CURRENT_GRID_CLASS
        y, _ = self.useable_space()
        self.rowOffset = MENU_WIDTH
        if MODE == "Vms":
            CURRENT_GRID_CLASS = instancesGrid.InstancesGrid
            menu_desc.append('Create new')
            menu_desc.append('Visual Graph')
        elif MODE == "INSTANCES-LBU":
            CURRENT_GRID_CLASS = instancesGrid.InstancesGridLBU
            menu_desc.append('CREATE NEW')
        elif MODE == "Security":
            CURRENT_GRID_CLASS = securityGroupsGrid.SecurityGroupsGrid
            menu_desc.append('Create new')
        elif MODE == "SECURITY-VM":
            CURRENT_GRID_CLASS = securityGroupsGrid.SecurityGroupsGridForOneInstance
            menu_desc.append('ADD SEC-GROUP')
        elif MODE == 'SECURITY-RULES':
            CURRENT_GRID_CLASS = securityRulesGrid.SecurityRulesGrid
            menu_desc.append('Create new')
            menu_desc.append('Add my ssh IP')
            if guiRules.RULES is not None and MODE in guiRules.RULES:
                for name in guiRules.RULES[MODE]:
                    menu_desc.append(name)
        elif MODE == 'Volumes':
            CURRENT_GRID_CLASS = volumesGrid.VolumeGrid
            menu_desc.append('Create new')
        elif MODE == 'VOLUMES-VM':
            CURRENT_GRID_CLASS = volumesGrid.VolumeGridForOneInstance
        elif MODE == 'Snapshots':
            CURRENT_GRID_CLASS = snapshotGrid.SnapshotGrid
            menu_desc.append('Create new')
        elif MODE == 'Images':
            CURRENT_GRID_CLASS = imageGrid.ImageGrid
            menu_desc.append('Filter')
            menu_desc.append('Create new')
        elif MODE == 'LoadBalancers':
            CURRENT_GRID_CLASS = loadbalancerGrid.loadbalancerGrid
            menu_desc.append('Create new')
        elif MODE == 'Nets':
            CURRENT_GRID_CLASS = vpcsGrid.vpcsGrid
            menu_desc.append('Create new')
        elif MODE == 'NetAccessPoints':
            CURRENT_GRID_CLASS = netAccesssPoint.Grid
            menu_desc.append('Create new')
        elif MODE == 'NetPeering':
            CURRENT_GRID_CLASS = netPeering.Grid
        elif MODE == 'GPUs':
            CURRENT_GRID_CLASS = flexibleGPU.Grid
        elif MODE == 'Subnets':
            CURRENT_GRID_CLASS = vpcsGrid.subnetGrid
            menu_desc.append('Create new')
        elif MODE == 'Nics':
            CURRENT_GRID_CLASS = nicsGrid.nicsGrid
        elif MODE == 'InternetServices':
            CURRENT_GRID_CLASS = internetServices.internetServicesGrid
        elif MODE == 'RouteTables':
            CURRENT_GRID_CLASS = routeTables.routeTablesGrid
        elif MODE == 'DhcpOptions':
            CURRENT_GRID_CLASS = dhcpOptions.dhcpOptionsGrid
        elif MODE == 'NatServices':
            CURRENT_GRID_CLASS = natServices.natServicesGrid
        elif MODE == 'Users':
            CURRENT_GRID_CLASS = userGrid.userGrid
        elif MODE == 'UserGroups':
            CURRENT_GRID_CLASS = userGrid.userGroupGrid
        elif MODE == 'PublicIps':
            CURRENT_GRID_CLASS = publicIps.publicIpsGrid
        elif MODE == 'Keypairs':
            CURRENT_GRID_CLASS = keyPairsGrid.KeyPairsGrid
            menu_desc.append('Create new')
        self.add_widget(
            mainMenu,
            form=self,
            relx=1,
            max_width=MENU_WIDTH,
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
            relx=GRID_START_COL,
            rely=2,
        )

    def create_new(self, _):
        global MODE
        if MODE == "Vms":
            self.parentApp.addForm("CREATE_VM", createVm.CreateVm, name="osc-tui")
            self.parentApp.switchForm("CREATE_VM")
        elif MODE == "Security":
            popup.newSecurityGroup(self)
        elif MODE == "Volumes":
            self.parentApp.addForm("CREATE_VOLUME", createVolume.CreateVolume, name="osc-tui")
            self.parentApp.switchForm("CREATE_VOLUME")
        elif MODE == "Snapshots":
            self.parentApp.addForm("CREATE_SNAPSHOT", createSnapshot.CreateSnapshot, name="osc-tui")
            self.parentApp.switchForm("CREATE_SNAPSHOT")
        elif MODE == "Keypairs":
            self.parentApp.addForm("CREATE_KEYPAIR", createKeyPair.CreateKeyPair, name="osc-tui")
            self.parentApp.switchForm("CREATE_KEYPAIR")
        elif MODE == "Images":
            self.parentApp.addForm("CREATE_Images", createImage.CreateImage, name="osc-tui")
            self.parentApp.switchForm("CREATE_Images")
        elif MODE == "LoadBalancers":
            self.parentApp.addForm("CREATE_LOADBALANCER", createLoadbalancer.CreateLoadbalancer, name="osc-tui")
            self.parentApp.switchForm("CREATE_LOADBALANCER")
        elif MODE == "Nets":
            self.parentApp.addForm("CREATE_VPCS", createVpcs.CreateVpcs, name="osc-tui")
            self.parentApp.switchForm("CREATE_VPCS")
        elif MODE == "NetAccessPoints":
            self.parentApp.addForm("CREATE_NET-ACCESS-POINT", createNetAccessPoint.CreateNetAccessPoint, name="osc-tui")
            self.parentApp.switchForm("CREATE_NET-ACCESS-POINT")
        
    
    def on_screen(self):
        super().on_screen()

    def draw_form(self):
        _, MAXX = self.curses_pad.getmaxyx()
        super().draw_form()
        MAXX, _ = self.curses_pad.getmaxyx()
        self.curses_pad.vline(1, LINE_SEPARATOR_COL, curses.ACS_VLINE, MAXX - 2)
    
    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("Cockpit", MainForm, name="osc-tui")
        self.parentApp.switchForm("Cockpit")

    def quit_key(self, key_val):
        main.kill_threads()
        self.parentApp.switchForm("MAIN")
        
    def key_reload(self, _):
        self.reload()

    def switch_to_volumes(self, _):
        global MODE
        MODE = "Volumes"
        self.reload()

    def switch_to_public_ips(self, _):
        global MODE
        MODE = "PublicIps"
        self.reload()

    def switch_to_instances(self, _):
        global MODE
        MODE = "Vms"
        self.reload()

    def switch_to_images(self, _):
        global MODE
        MODE = "Images"
        self.reload()

    def switch_to_security_grid(self, _):
        global MODE
        MODE = "Security"
        self.reload()

    def switch_to_nets(self, _):
        global MODE
        MODE = "Nets"
        self.reload()
    
    def switch_to_keypairs(self, _):
        global MODE
        MODE = "Keypairs"
        self.reload()

    def set_up_handlers(self):
        super().set_up_handlers()
        
        self.add_handlers({"q": self.quit_key})
        self.add_handlers({"^Q": quit})
        self.add_handlers({"h": popup.showHelp})
        self.add_handlers({"?": popup.showHelp})
        self.add_handlers({"/": popup.slashSearch})
        self.add_handlers({"C": self.create_new})
        self.add_handlers({"V": self.switch_to_volumes})
        self.add_handlers({"I": self.switch_to_instances})
        self.add_handlers({"M": self.switch_to_images})
        self.add_handlers({"P": self.switch_to_public_ips})
        self.add_handlers({"S": self.switch_to_security_grid})
        self.add_handlers({"T": self.switch_to_nets})
        self.add_handlers({"K": self.switch_to_keypairs})
        self.add_handlers({
            "r"             : self.key_reload,
            curses.KEY_F5   : self.key_reload
        })

