import curses
from threading import Thread
import os
import json
import datetime

import osc_npyscreen
import osc_npyscreen.fmPopup
import osc_npyscreen.wgmultiline
import pyperclip
from osc_npyscreen import *

import requests
from osc_tui import main
from osc_tui import mainForm

from osc_sdk_python import Gateway

SUBNETID = None
ROUTE = None


class ConfirmCancelPopup(osc_npyscreen.fmPopup.ActionPopup):
    term_size = os.get_terminal_size()
    DEFAULT_COLUMNS = 100
    SHOW_ATX = int(term_size.columns / 2 - DEFAULT_COLUMNS /2)
    def on_ok(self):
        self.value = True

    def on_cancel(self):
        self.value = False


class displayPopup(osc_npyscreen.fmPopup.Popup):
    term_size = os.get_terminal_size()
    DEFAULT_COLUMNS = 100
    OK_BUTTON_TEXT = 'BACK'
    SHOW_ATX = int(term_size.columns / 2 - DEFAULT_COLUMNS /2)
    def __init__(self, *args, **keywords):
        if "lines" in keywords:
            self.DEFAULT_LINES = keywords["lines"]
        super().__init__(*args, **keywords)

    def on_ok(self):
        self.editing = False
        self.value = True

class displayPopupWide(osc_npyscreen.fmPopup.PopupWide):
    term_size = os.get_terminal_size()
    OK_BUTTON_TEXT = 'BACK'
    DEFAULT_LINES = term_size.lines - 2

    def on_ok(self):
        self.editing = False
        self.value = True


def readString(name='', form_color='STANDOUT'):
    F = ConfirmCancelPopup(name=name, color=form_color)
    F.preserve_selected_widget = True
    tf = F.add(osc_npyscreen.Textfield)
    tf.width = tf.width - 1
    tf.value = ""
    F.edit()
    if F.value is True:
        return tf.value
    else:
        return None


def readAKSK(form_color='STANDOUT'):
    while True:
        F = ConfirmCancelPopup(name='New profile', color=form_color)
        F.preserve_selected_widget = True
        name = F.add(osc_npyscreen.TitleText, name="NAME:")
        ak = F.add(osc_npyscreen.TitleText, name="ACCESS KEY:")
        sk = F.add(osc_npyscreen.TitlePassword, name="SECRET KEY:")
        regions = requests.post(
            "https://api.eu-west-2.outscale.com/api/latest/ReadRegions")
        regions_list = []
        if regions == 200:
            regions = regions.json()
            for region in regions["Regions"]:
                regions_list.append(region["RegionName"])
        else:
            regions_list = "eu-west-2", "us-east-2", "us-west-1", "cn-southeast-1"
        global REGION
        REGION = F.add_widget(
            osc_npyscreen.TitleCombo,
            name="REGION:",
            values=regions_list,
            value=0,
        )

        F.edit()
        if F.value is True:
            if name.value != '' and ak.value != '' and sk.value != '':
                return {
                    name.value: {
                        'access_key': ak.value,
                        'secret_key': sk.value,
                        'region': REGION.values[REGION.value]
                    }
                }
            else:
                osc_npyscreen.notify_confirm(
                    "Please check that you filled all fields.", "ERROR")
        else:
            return None

def displayInfoPopup(popupName, cb):
    F = displayPopupWide(popupName)
    F.preserve_selected_widget = True
        
    ft = F.add_widget(
        osc_npyscreen.Pager,
    )
    ft.values = json.dumps(cb, indent=2).split("\n")
        
    def ok():
        exit()

    F.on_ok = ok
    F.edit()


def editInstance(form, instance, form_color='STANDOUT'):
    status = instance[0]
    id = instance[2]
    name = instance[1]
    F = displayPopup(name=name + ' (' + id + ')', color=form_color, lines=20)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False
    F.on_ok = exit
    # Buttons about VMs
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
    run_stop = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="RUN",
    )
    restart = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="RESTART",
    )
    force_stop = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="FORCE STOP",
    )
    terminate = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="TERMINATE",
    )
    copy_ip = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="COPY IP",
    )
    security = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="SECURITY",
    )
    volumes = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="VOLUMES",
    )
    lbu = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="ADD TO LBU",
    )
    image_from = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="CREATE IMAGE FROM VM",
    )
    # Now managing actions and wich buttons to hide or not.
    force_stop.hidden = (True if status == "stopped"
                         or status == "terminated" else False)
    restart.hidden = False if status == "running" else True
    security.hidden = True if status == "terminated" else False
    copy_ip.hidden = (True if status == "terminated" or status == "stopped"
                      else False)
    terminate.hidden = True if status == "terminated" else False
    if status == "running" or status == "stopped":
        run_stop.name = "RUN" if status == "stopped" else "STOP"
        run_stop.hidden = False
    else:
        run_stop.hidden = True
    if status == "terminated":
        security.hidden = True
    else:
        security.hidden = False
    run_stop.update()

    # Operations availables:
    def info_vm():
        exit()
        popupName = "Vm Info " + name + ", id: " + id
        vm = main.GATEWAY.ReadVms(form=form, Filters={"VmIds": [id]})
        vm = vm["Vms"][0]
        displayInfoPopup(popupName, vm)
       
    def start_vm():
        main.GATEWAY.StartVms(form=form, VmIds=[id])
        form.current_grid.h_refresh(None)
        exit()

    def terminate_vm():
        main.kill_threads()
        if osc_npyscreen.notify_ok_cancel(
                "Do you really want to terminate this vm:\nName: " + name +
                "\nID: " + id,
                "VM Termination",
        ):
            main.GATEWAY.DeleteVms(form=form, VmIds=[id])
        form.current_grid.h_refresh(None)
        exit()

    def stop_vm():
        main.GATEWAY.StopVms(form=form, VmIds=[id])
        form.current_grid.h_refresh(None)
        exit()

    def force_stop_vm():
        main.GATEWAY.StopVms(form=form, ForceStop=True, VmIds=[id])
        form.current_grid.h_refresh(None)
        exit()

    def restart_vm():
        main.GATEWAY.RebootVms(form=form, VmIds=[id])
        exit()

    def sg():
        exit()
        main.kill_threads()
        main.VM = main.VMs[id]
        mainForm.MODE = 'SECURITY-VM'
        form.reload()

    def _copy_ip():
        pyperclip.copy(instance[5])
        exit()

    def volumes_cb():
        main.VM = main.VMs[id]
        mainForm.MODE = 'VOLUMES-VM'
        exit()
        form.reload()

    def image_from_cb():
        this_name = name
        this_name = this_name + " " + datetime.datetime.today().strftime('%Y-%m-%d')
        mainForm.MODE = 'Images'
        main.GATEWAY.CreateImage(VmId=id, NoReboot=True, ImageName=this_name)
        exit()
        form.reload()

    def add_to_lbu():
        osc_npyscreen.notify_confirm("Not implemented yet :/")

    info.whenPressed = info_vm
    copy_ip.whenPressed = copy_ip
    run_stop.whenPressed = start_vm if status == "stopped" else stop_vm
    force_stop.whenPressed = force_stop_vm
    restart.whenPressed = restart_vm
    security.whenPressed = sg
    terminate.whenPressed = terminate_vm
    copy_ip.whenPressed = _copy_ip
    volumes.whenPressed = volumes_cb
    image_from.whenPressed = image_from_cb
    lbu.whenPressed = add_to_lbu
    F.edit()


def selectRouteTable(form, rt, form_color='STANDOUT'):
    id = rt[0]
    F = displayPopup(id, color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    def info_rt():
        exit()
        popupName = "Route Table Info id: " + id
        sg = main.GATEWAY.ReadRouteTables(form=form, Filters={"RouteTableIds": [id]})
        sg = sg["RouteTables"][0]
        displayInfoPopup(popupName, sg)

    info.whenPressed = info_rt
    F.edit()
    form.current_grid.display()

def selectPublicIp(form, pip, form_color='STANDOUT'):
    id = pip[0]
    F = displayPopup(id, color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    def info_pip():
        exit()
        popupName = "Public Ip Info id: " + id
        ips = main.GATEWAY.ReadPublicIps(form=form, Filters={"PublicIpIds": [id]})
        ips = ips["PublicIps"][0]
        displayInfoPopup(popupName, ips) 

    info.whenPressed = info_pip
    F.edit()
    form.current_grid.display()

def selectNic(form, nic, form_color='STANDOUT'):
    id = nic[0]
    F = displayPopup(id, color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    def info_nic():
        exit()
        popupName = "Nic Info id: " + id
        nic = main.GATEWAY.ReadNics(form=form, Filters={"NicIds": [id]})
        nic = nic["Nics"][0]
        displayInfoPopup(popupName, nic) 
        
    info.whenPressed = info_nic
    F.edit()
    form.current_grid.display()

def selectInternetService(form, iserv, form_color='STANDOUT'):
    id = iserv[0]
    F = displayPopup(id, color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    def info_is():
        exit()
        popupName = "Internet Service Info id: " + id
        iserv = main.GATEWAY.ReadInternetServices(form=form, Filters={"InternetServiceIds": [id]})
        iserv = iserv["InternetServices"][0]
        displayInfoPopup(popupName, iserv)

    info.whenPressed = info_is
    F.edit()
    form.current_grid.display()

def selectNatService(form, nat, form_color='STANDOUT'):
    id = nat[0]
    F = displayPopup(id, color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    def info_nat():
        exit()
        popupName = "Nat Service Info id: " + id
        nat = main.GATEWAY.ReadNatServices(form=form, Filters={"NatServiceIds": [id]})
        nat = nat["NatServices"][0]
        displayInfoPopup(popupName, nat)        

    info.whenPressed = info_nat
    F.edit()
    form.current_grid.display()

def editDhcpOptions(form, dopt, form_color='STANDOUT'):
    id = dopt[0]
    F = displayPopup(id, color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    def info_dopt():
        exit()
        popupName = "DHCP Options Info id: " + id
        dopt = main.GATEWAY.ReadDhcpOptions(form=form, Filters={"DhcpOptionsSetIds": [id]})
        dopt = dopt["DhcpOptionsSets"][0]
        displayInfoPopup(popupName, dopt)

    info.whenPressed = info_dopt
    F.edit()
    form.current_grid.display()

def editSecurityGroup(form, sg, form_color='STANDOUT'):
    name = sg[1]
    id = sg[0]
    main.SECURITY_GROUP = id
    F = displayPopup(name=name + ' (' + id + ')', color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
    def info_sg():
        exit()
        popupName = "SG Info " + name + ", id: " + id
        sg = main.GATEWAY.ReadSecurityGroups(form=form, Filters={"SecurityGroupIds": [id]})
        sg = sg["SecurityGroups"][0]
        displayInfoPopup(popupName, sg)

    edit = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        exit()
        mainForm.MODE = 'SECURITY-RULES'
        form.reload()

    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )

    def delete_cb():
        try:
            main.GATEWAY.DeleteSecurityGroup(form=form, SecurityGroupId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()

    info.whenPressed = info_sg
    edit.whenPressed = edit_cb
    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.display()


def manageSecurityGroup(form, sg, form_color='STANDOUT'):
    name = sg[1]
    id = sg[0]
    main.SECURITY_GROUP = id
    F = displayPopup(name=name + ' (' + id + ')', color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    edit = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        exit()
        mainForm.MODE = 'SECURITY-RULES'
        form.reload()

    remove = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="REMOVE FROM INSTANCE",
    )

    def remove_cb():
        groups = main.VM["SecurityGroups"]
        values = list()
        for g in groups:
            if id != g["SecurityGroupId"]:
                values.append(g["SecurityGroupId"])
        main.GATEWAY.UpdateVm(
            form=form,
            VmId=main.VM["VmId"],
            SecurityGroupIds=values)
        form.current_grid.h_refresh(None)
        exit()
    edit.whenPressed = edit_cb
    remove.whenPressed = remove_cb
    F.edit()
    form.current_grid.display()


def editInstanceInLBU(form, sg, form_color='STANDOUT'):
    name = sg[1]
    id = sg[2]
    F = displayPopup(name=name + ' (' + id + ')', color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    edit = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        exit()
        mainForm.MODE = 'SECURITY-RULES'
        form.reload()

    remove = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="REMOVE FROM LBU",
    )

    def remove_cb():
        main.GATEWAY.DeregisterVmsInLoadBalancer(
            **{'BackendVmIds': [id], 'LoadBalancerName': main.LBU})
        form.current_grid.h_refresh(None)
        exit()
    edit.whenPressed = edit_cb
    remove.whenPressed = remove_cb
    F.edit()
    form.current_grid.display()


def addSecurityGroupToVm(form, form_color='STANDOUT'):
    F = ConfirmCancelPopup(name='Add New Security Group', color=form_color)
    F.preserve_selected_widget = True
    groups = main.VM["SecurityGroups"]
    vm_sg = list()
    for g in groups:
        vm_sg.append(g["SecurityGroupId"])
    groups = main.GATEWAY.ReadSecurityGroups(form=form)["SecurityGroups"]
    values = list()
    for g in groups:
        if not g["SecurityGroupId"] in vm_sg:
            values.append(g["SecurityGroupId"])
    new_sg = F.add_widget(
        osc_npyscreen.TitleCombo,
        name="CHOOSE SECURITY GROUP",
        values=values,
        value=0,
    )

    def exit():
        groups = main.VM["SecurityGroups"]
        values = list()
        for g in groups:
            values.append(g["SecurityGroupId"])
        values.append(new_sg.values[new_sg.value])
        main.GATEWAY.UpdateVm(
            form=form,
            VmId=main.VM["VmId"],
            SecurityGroupIds=values)
        F.editing = False

    F.on_ok = exit
    F.edit()
    form.current_grid.h_refresh(None)
    form.current_grid.display()


def editSecurityGroupRule(form, rule, form_color='STANDOUT'):
    dir = rule[0]
    protocol = "-1" if rule[1] == "all" else rule[1]
    from_port = None if rule[2] == "all" else rule[2]
    to_port = None if rule[3] == "all" else rule[3]
    ip_range = rule[4]
    main.SECURITY_RULE = id
    title = "Rule: " + str(protocol) + " from: " + str(
        from_port) + " to: " + str(to_port) + " with ip: " + str(ip_range)
    F = displayPopup(name=title, color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    btn_delete = F.add_widget(osc_npyscreen.ButtonPress, name="DELETE")

    def delete():
        if from_port and to_port:
            main.GATEWAY.DeleteSecurityGroupRule(
                FromPortRange=from_port,
                IpProtocol=protocol,
                IpRange=ip_range,
                ToPortRange=to_port,
                SecurityGroupId=main.SECURITY_GROUP,
                Flow=dir,
            )
        else:
            main.GATEWAY.DeleteSecurityGroupRule(
                IpProtocol=protocol,
                IpRange=ip_range,
                SecurityGroupId=main.SECURITY_GROUP,
                Flow=dir,
            )
        form.current_grid.h_refresh(None)
        exit()

    btn_delete.whenPressed = delete
    F.edit()
    form.current_grid.ensure_cursor_on_display_down_right(None)
    form.current_grid.ensure_cursor_on_display_up(None)
    form.current_grid.display()


def newSecurityGroupRule(form, form_color='STANDOUT'):
    osc_npyscreen.ActionPopup.DEFAULT_LINES = 15
    F = ConfirmCancelPopup(name='New Security Rule', color=form_color)

    F.preserve_selected_widget = True
    F.add_widget(osc_npyscreen.Textfield, value="From PORT:", editable=False)
    from_port = F.add_widget(osc_npyscreen.Textfield, value="22", editable=True)
    F.add_widget(osc_npyscreen.Textfield, value="To PORT:", editable=False)
    to_port = F.add_widget(osc_npyscreen.Textfield, value="22", editable=True)
    protocole = F.add(
        osc_npyscreen.TitleSelectOne,
        max_height=4,
        value=[0, ],
        name="Protocol",
        values=["tcp", "udp", "icmp", "all"],
        scroll_exit=True,
    )
    F.add_widget(osc_npyscreen.Textfield, value="IP:", editable=False)
    ip = F.add_widget(
        osc_npyscreen.Textfield, value=main.IP + "/32", editable=True
    )

    def exit():
        try:
            main.GATEWAY.CreateSecurityGroupRule(
                FromPortRange=int(from_port.value),
                IpProtocol='-1' if protocole.get_selected_objects(
                )[0] == 'all' else protocole.get_selected_objects()[0],
                IpRange=ip.value,
                ToPortRange=int(to_port.value),
                SecurityGroupId=main.SECURITY_GROUP,
                Flow='Inbound'
            )
        except BaseException:
            raise
        F.editing = False
        osc_npyscreen.ActionPopup.DEFAULT_LINES = 12

    F.on_ok = exit
    F.edit()
    form.current_grid.h_refresh(None)
    form.current_grid.display()


def newSecurityGroup(form, form_color='STANDOUT'):
    F = ConfirmCancelPopup(name='New Security Group', color=form_color)

    F.preserve_selected_widget = True
    F.add_widget(osc_npyscreen.Textfield, value="Name", editable=False)
    name = F.add_widget(osc_npyscreen.Textfield, value="NewName", editable=True)

    def exit():
        try:
            main.GATEWAY.CreateSecurityGroup(
                Description='desc',
                SecurityGroupName=name.value
            )
        except BaseException:
            raise
        F.editing = False

    F.on_ok = exit
    F.edit()
    form.current_grid.h_refresh(None)
    form.current_grid.display()

def addFilter(form, form_color='STANDOUT'):
    F = ConfirmCancelPopup(name='Filter', color=form_color)
    F.preserve_selected_widget = True
    F.add_widget(osc_npyscreen.Textfield, value="Name Filter (exemple: 'Arch *'):", editable=False)
    name = F.add_widget(osc_npyscreen.Textfield, value="*", editable=True)

    def exit():
        form.current_grid.h_refresh(None, name_filter=name.value)
        form.current_grid.display()
        F.editing = False

    F.on_ok = exit
    F.edit()
    

def editVolume(form, volume, form_color='STANDOUT'):
    id = volume[0]
    type = volume[1]
    size = volume[3]
    vm_id = volume[5]
    #device_name = volume[6]
    #iops = volume[7]

    F = displayPopup(
        name="{} ({}), {} gib, linked to: {}".format(id, type, size, vm_id))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
    edit = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="EDIT",
    )
    
    def edit_cb():
        exit()
        mainForm.MODE = "Volume-Edit"
        mainForm.swicthToVolumeEdit(form, id, volume)
        return

    def link_cb():
        exit()
        mainForm.MODE = "Volume-Link"
        mainForm.swicthToVolumeLink(form, id, volume)
        return

    def unlink_cb():
        main.GATEWAY.UnlinkVolume(VolumeId=id)
        exit()
        return

    if vm_id == "Unlinked":
        link = F.add_widget(
            osc_npyscreen.ButtonPress,
            name="LINK"
        )
        link.whenPressed = link_cb
    else:
        unlink = F.add_widget(
            osc_npyscreen.ButtonPress,
            name="UNLINK",
        )
        unlink.whenPressed = unlink_cb

    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )

    def info_cb():
        exit()
        popupName = "Volume Info " + id
        cb = main.GATEWAY.ReadVolumes(form=form, Filters={"VolumeIds": [id]})
        cb = cb["Volumes"][0]
        displayInfoPopup(popupName, cb) 
        
    def delete_cb():
        try:
            main.GATEWAY.DeleteVolume(VolumeId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()

    info.whenPressed = info_cb
    edit.whenPressed = edit_cb
    delete.whenPressed = delete_cb

    F.edit()
    form.current_grid.display()


def editSnapshot(form, snapshot, form_color='STANDOUT'):
    id = snapshot[0]
    # description = snapshot[1]
    size = snapshot[2]
    volume_id = snapshot[3]

    F = displayPopup(name="{} ({} gib), volume: {}".format(id, size, volume_id))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit

    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    def info_snap():
        exit()
        popupName = "Snapshot Info id: " + id
        sg = main.GATEWAY.ReadSnapshots(form=form, Filters={"SnapshotIds": [id]})
        sg = sg["Snapshots"][0]
        displayInfoPopup(popupName, sg)

    edit = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        # SNAPSHOT-EDIT not yet implemented
        # mainForm.MODE = "SNAPSHOT-EDIT"
        # form.reload()
        exit()

    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )

    def delete_cb():
        try:
            main.GATEWAY.DeleteSnapshot(SnapshotId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()

    info.whenPressed = info_snap
    edit.whenPressed = edit_cb
    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.display()


def editFlexibleGpu(form, flexibleGpu, form_color='STANDOUT'):
    name = flexibleGpu[0]
    F = displayPopup(name="{}".format(name))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False


    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )

    def info_cb():
        exit()
        popupName = "FlexibleGpu Info " + name
        cb = main.GATEWAY.ReadFlexibleGpus(form=form, Filters={"FlexibleGpuIds": [name]})
        cb = cb["FlexibleGpus"][0]
        displayInfoPopup(popupName, cb) 
        
    def delete_cb():
        main.GATEWAY.DeleteFlexibleGpu(FlexibleGpuId=name)
        form.current_grid.h_refresh(None)
        exit()

    info.whenPressed = info_cb
    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.display()
    form.current_grid.refresh()


def editLoadbalancer(form, loadbalancer, form_color='STANDOUT'):
    name = loadbalancer[0]
    F = displayPopup(name="{}".format(name))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    def instances_registered():
        exit()
        mainForm.MODE = 'INSTANCES-LBU'
        form.reload()

    F.on_ok = exit

    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
    reg = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="REGISTERED VMs",
    )
    reg.whenPressed = instances_registered
    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )

    def info_cb():
        exit()
        popupName = "LoadBalancer Info " + name
        cb = main.GATEWAY.ReadLoadBalancers(form=form, Filters={"LoadBalancerNames": [name]})
        cb = cb["LoadBalancers"][0]
        displayInfoPopup(popupName, cb) 
        
    def delete_cb():
        main.GATEWAY.DeleteLoadBalancer(LoadBalancerName=name)
        form.current_grid.h_refresh(None)
        exit()

    info.whenPressed = info_cb
    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.display()
    form.current_grid.refresh()


def editVpcs(form, vpcs, form_color='STANDOUT'):
    name = vpcs[0]
    global SUBNETID
    SUBNETID = vpcs[0]
    F = displayPopup(name="{}".format(name))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit

    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
    def info_net():
        exit()
        popupName = "Net Info Id: " + name
        sg = main.GATEWAY.ReadNets(form=form, Filters={"NetIds": [name]})
        sg = sg["Nets"][0]
        displayInfoPopup(popupName, sg)

    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )
    read_subnet = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="READ SUBNET",
    )

    def delete_cb():
        main.GATEWAY.DeleteNet(NetId=name)
        form.current_grid.h_refresh(None)
        exit()

    def subnetRead():
        exit()
        mainForm.MODE = 'Subnets'
        form.reload()

    info.whenPressed = info_net
    delete.whenPressed = delete_cb
    read_subnet.whenPressed = subnetRead
    F.edit()
    form.current_grid.display()


def associateRouteTable(form, subnet):
    F = displayPopup(name="{associate route table}")
    F.preserve_selected_widget = True

    def exit():
        F.editing = False
    F.on_ok = exit
    global ROUTE
    route_tables = main.GATEWAY.ReadRouteTables()["RouteTables"]
    route_tables_vals = []
    for route_table in route_tables:
        route_tables_vals.append(route_table["RouteTableId"])
    ROUTE = F.add_widget(
        osc_npyscreen.TitleCombo,
        name="CHOOSE A ROUTE TABLE",
        values=route_tables_vals,
        value=ROUTE.get_value() if ROUTE else 0,
    )
    associate_button = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="ASSOCIATE",
    )

    def associate():
        id_route = ROUTE.get_values()[ROUTE.get_value()]
        main.GATEWAY.LinkRouteTable(
            RouteTableId=id_route, SubnetId=subnet)
        exit()
    associate_button.whenPressed = associate
    F.edit()
    form.current_grid.display()
    form.current_grid.refresh()


def editSubnet(form, subnet, form_color='STANDOUT'):
    name = subnet[0]
    F = displayPopup(name="{}".format(name))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit

    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
    def info_subnet():
        exit()
        popupName = "Subnet Info Id: " + name
        sg = main.GATEWAY.ReadSubnets(form=form, Filters={"SubnetIds": [name]})
        sg = sg["Subnets"][0]
        displayInfoPopup(popupName, sg)

    test = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="ASSOCIATE ROUTE TABLE"
    )
    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )

    def associateRoutetable():
        associateRouteTable(form, name)
        form.current_grid.h_refresh(None)
        exit()

    def delete_cb():
        main.GATEWAY.DeleteSubnet(SubnetId=name)
        form.current_grid.h_refresh(None)
        exit()

    info.whenPressed = info_subnet
    delete.whenPressed = delete_cb
    test.whenPressed = associateRoutetable
    F.edit()
    form.current_grid.display()
    form.current_grid.refresh()


loaderPause = False

def pauseLoader():
    global loaderPause
    loaderPause = True

def startLoading(form, refresh):
    term_size = os.get_terminal_size()
    class PendingPopup(fmForm.Form):
        DEFAULT_LINES = 7
        DEFAULT_COLUMNS = 12
        SHOW_ATX = int(term_size.columns / 2 - DEFAULT_COLUMNS /2)
        SHOW_ATY = int(term_size.lines / 2 - DEFAULT_LINES / 2)

    def notify(message, title="Loading", form_color='STANDOUT',
               wrap=True, wide=False,
               ):
        F = PendingPopup(name=title, color=form_color)
        F.preserve_selected_widget = True
        mlw = F.add(wgmultiline.Pager,)
        message = message.split('\n')
        mlw.values = message
        F.display()
    global waiting
    waiting = True

    def capsule():
        refresh()
        global waiting
        waiting = False

    thread = Thread(target=capsule)
    thread.start()
    global loaderPause
    i = 0
    while waiting:
        frames = [
            "   |/\n" +
            "   +\n",

            "  \|  \n" +
            "   +\n",

            "  \\ \n" +
            " --+ \n",

            "    \n" +
            " --+ \n" +
            "  /",

            " \n" +
            "   + \n" +
            "  /|",

            "  \n" +
            "   + \n" +
            "   |\\",

            "  \n" +
            "   +--\n" +
            "    \\",

            "    /\n" +
            "   +-- \n"
        ]
        if loaderPause is False:
            notify(frames[i], wide=True)
        i = i + 1
        if(i >= len(frames)):
            i = 0
        curses.napms(150)
        curses.flushinp()
    loaderPause = False
    thread.join()


def editKeypair(form, line, form_color='STANDOUT'):
    name = line[0]
    #fingerprint = line[1]

    F = displayPopup(name="Keypair: {}".format(name))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit

    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )

    def info_cb():
        exit()
        popupName = "Keypair Info " + name
        cb = main.GATEWAY.ReadKeypairs(form=form, Filters={"KeypairNames": [name]})
        cb = cb["Keypairs"][0]
        displayInfoPopup(popupName, cb)
       
    def delete_cb():
        delete = osc_npyscreen.notify_ok_cancel(
            "You will delete permanently the keypair named " + name, "Warning")
        if delete:
            try:
                main.GATEWAY.DeleteKeypair(form=form, KeypairName=name)
            except BaseException:
                raise
            form.current_grid.h_refresh(None)
            exit()

    info.whenPressed = info_cb
    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.display()


def editImage(form, image, form_color='STANDOUT'):
    name = image[0]
    id = image[1]

    F = displayPopup(name="Image: {} {}".format(id, name))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False
    F.on_ok = exit

    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE",
    )

    def info_img():
        exit()
        popupName = "Image Info id: " + id
        sg = main.GATEWAY.ReadImages(form=form, Filters={"ImageIds": [id]})
        sg = sg["Images"][0]
        displayInfoPopup(popupName, sg)

    info.whenPressed = info_img


    def delete_cb():
        try:
            main.GATEWAY.DeleteImage(ImageId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()

    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.display()

def editNetAccessPoint(form, line, form_color='STANDOUT'):
    id = line[0]

    F = displayPopup(name="Net Access Point: {}".format(id))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit

    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )
        
    edit = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="EDIT"
    )
    
    delete = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="DELETE"
    )

    def info_cb():
        exit()
        popupName = "NetAccessPoint Info id: " + id
        cb = main.GATEWAY.ReadNetAccessPoints(form=form, Filters={"NetAccessPointIds": [id]})
        cb = cb["NetAccessPoints"][0]
        displayInfoPopup(popupName, cb)
       
    def edit_cb():
        form.current_grid.h_refresh(None)
        exit()
        editRouteTable(form, id) 

    def delete_cb():
        try:
            main.GATEWAY.DeleteNetAccessPoint(NetAccessPointId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()

    info.whenPressed = info_cb
    edit.whenPressed = edit_cb 
    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.display()

def editNetPeering(form, netp, form_color='STANDOUT'):
    id = netp[0]
    F = displayPopup(id, color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    info = F.add_widget(
        osc_npyscreen.ButtonPress,
        name="INFO",
    )

    def info_netp():
        exit()
        popupName = "Net Peering Info id: " + id
        netp = main.GATEWAY.ReadNetPeerings(form=form, Filters={"NetPeeringIds": [id]})
        netp = netp["NetPeerings"][0]
        displayInfoPopup(popupName, netp)

    info.whenPressed = info_netp
    F.edit()
    form.current_grid.display()

def editRouteTable(form, point_id, form_color='STANDOUT'):
    global ROUTE_MULTISELECT 
    global net_route_table 
    global all_route_tables 

    id = point_id

    F = ConfirmCancelPopup(name="Edit route table(s): {}".format(id))
    F.preserve_selected_widget = True
    F.DEFAULT_LINES = 40

    def exit():
        F.editing = False

    def ok():
        new_route =  [
            ROUTE_MULTISELECT.get_values()[i]
            for i in ROUTE_MULTISELECT.get_value()
        ]
        
        deleted_route = []
        added_route = []

        for r in new_route:
            if r not in net_route_table:
                added_route.append(r)
                
        for route in all_route_tables:
            if route not in new_route:
                if route in net_route_table:
                    deleted_route.append(route)

        if not deleted_route and not added_route:
            osc_npyscreen.notify_confirm("Nothing as changed")
        else:
            res = main.GATEWAY.UpdateNetAccessPoint(
                NetAccessPointId=id,
                AddRouteTableIds=added_route,
                RemoveRouteTableIds=deleted_route
            )

            if "Error" in res:
                osc_npyscreen.notify_confirm(str(res["Errors"]))
            else:
                osc_npyscreen.notify_confirm(
                    "Route table(s) changed succesfully"
                )
                
            exit()
    
    F.on_ok = ok
    F.on_cencel = exit

    net_access_point = main.GATEWAY.ReadNetAccessPoints(
        form=form,
        Filters={'NetAccessPointIds':[id]}
    )['NetAccessPoints']
    net_route_table = net_access_point[0]['RouteTableIds']

    routes_reply = main.GATEWAY.ReadRouteTables(form=form)['RouteTables']
    all_route_tables = []
    for r in routes_reply:
        all_route_tables.append(r['RouteTableId'])

    selected_routes = []
    for r in net_route_table:
        for index, route in enumerate(all_route_tables):
            if r == route:
                selected_routes.append(index)

    ROUTE_MULTISELECT = F.add_widget(
        osc_npyscreen.TitleMultiSelect,
        name="SELECT ROUTE TABLE(S)",
        value=selected_routes,
        values=all_route_tables,
        max_height=4,
        scroll_exit=True
    )
    F.edit()
    form.current_grid.display()


def slashSearch(arg):
    form_color='STANDOUT'
    F = ConfirmCancelPopup(name='Search', color=form_color)
    F.preserve_selected_widget = True
    F.add_widget(osc_npyscreen.Textfield, value="Search:", editable=False)
    F.add_widget(osc_npyscreen.Textfield, value="(Empty string to reset)", editable=False)
    name = F.add_widget(osc_npyscreen.Textfield, value="", editable=True)

    def exit():
        main.SEARCH_FILTER=name.value
        if main.CURRENT_GRID:
            g = main.CURRENT_GRID
            g.h_refresh(None, skip_call=True)
            g.display()
        F.editing = False
    F.on_ok = exit
    F.edit()
    

def showHelp(arg):
    F = displayPopup(name = "Help")
    F.preserve_selected_widget = True

    ft = F.add_widget(
        osc_npyscreen.Pager,
        )
    ft.values = [
        "Return to profile  : q",
        "Exit               : Ctrl+Q",
        "Refresh            : F5 or r",
        "Search in Fields   : /",
        "search in Menu     : l",
        "Help               : h",
        "Create New         : C",
        "Switch to Vms      : I",
        "Switch to Volumes  : V",
        "Switch to Images   : M",
        "Switch to PublicIps: P",
        "Switch to Security : S",
        "Switch to Nets     : T",
        "Switch to Keypairs : K\n",
    ]
    
    def ok():
        exit()

    F.on_ok = ok
    F.edit()

def errorPopup(message):
    F = displayPopup(name = "Error")
    F.preserve_selected_widget = True

    ft = F.add_widget(
        osc_npyscreen.Pager,
        )
    ft.values = [message]
    
    def ok():
        exit()

    F.on_ok = ok
    F.edit()
