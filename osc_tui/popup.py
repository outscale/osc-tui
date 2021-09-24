import curses
import textwrap
from threading import Thread
import os

import npyscreen
import npyscreen.fmPopup
import npyscreen.wgmultiline
import pyperclip
from npyscreen import *

import requests
import main
import mainForm

SUBNETID = None
ROUTE = None


class ConfirmCancelPopup(npyscreen.fmPopup.ActionPopup):
    term_size = os.get_terminal_size()
    DEFAULT_COLUMNS = 100
    SHOW_ATX = int(term_size.columns / 2 - DEFAULT_COLUMNS /2)
    def on_ok(self):
        self.value = True

    def on_cancel(self):
        self.value = False


class displayPopup(npyscreen.fmPopup.Popup):
    term_size = os.get_terminal_size()
    DEFAULT_COLUMNS = 100
    SHOW_ATX = int(term_size.columns / 2 - DEFAULT_COLUMNS /2)
    def on_ok(self):
        self.editing = False
        self.value = True


def readString(form_color='STANDOUT'):

    F = ConfirmCancelPopup(name='', color=form_color)
    F.preserve_selected_widget = True
    tf = F.add(npyscreen.Textfield)
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
        name = F.add(npyscreen.TitleText, name="NAME:")
        ak = F.add(npyscreen.TitleText, name="ACCESS KEY:")
        sk = F.add(npyscreen.TitleText, name="SECRET KEY:")
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
            npyscreen.TitleCombo,
            name="REGION:",
            values=regions_list,
            value=0,
        )
        #ak.width = ak.width - 1
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
                npyscreen.notify_confirm(
                    "Please check that you filled all fields.", "ERROR")
        else:
            return None


def editInstance(form, instance, form_color='STANDOUT'):
    status = instance[0]
    id = instance[2]
    name = instance[1]
    F = displayPopup(name=name + ' (' + id + ')', color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False
    F.on_ok = exit
    # Buttons about VMs
    run_stop = F.add_widget(
        npyscreen.ButtonPress,
        name="RUN",
    )
    restart = F.add_widget(
        npyscreen.ButtonPress,
        name="RESTART",
    )
    force_stop = F.add_widget(
        npyscreen.ButtonPress,
        name="FORCE STOP",
    )
    terminate = F.add_widget(
        npyscreen.ButtonPress,
        name="TERMINATE",
    )
    copy_ip = F.add_widget(
        npyscreen.ButtonPress,
        name="COPY IP",
    )
    security = F.add_widget(
        npyscreen.ButtonPress,
        name="SECURITY",
    )
    volumes = F.add_widget(
        npyscreen.ButtonPress,
        name="VOLUMES",
    )
    lbu = F.add_widget(
        npyscreen.ButtonPress,
        name="ADD TO LBU",
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
    def start_vm():
        main.GATEWAY.StartVms(form=form, VmIds=[id])
        form.current_grid.h_refresh(None)
        exit()

    def terminate_vm():
        main.kill_threads()
        if npyscreen.notify_ok_cancel(
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

    def add_to_lbu():
        npyscreen.notify_confirm("Not implemented yet :/")

    copy_ip.whenPressed = copy_ip
    run_stop.whenPressed = start_vm if status == "stopped" else stop_vm
    force_stop.whenPressed = force_stop_vm
    restart.whenPressed = restart_vm
    security.whenPressed = sg
    terminate.whenPressed = terminate_vm
    copy_ip.whenPressed = _copy_ip
    volumes.whenPressed = volumes_cb
    lbu.whenPressed = add_to_lbu
    F.edit()


def editSecurityGroup(form, sg, form_color='STANDOUT'):
    name = sg[1]
    id = sg[0]
    main.SECURITY_GROUP = id
    F = displayPopup(name=name + ' (' + id + ')', color=form_color)
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    edit = F.add_widget(
        npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        exit()
        mainForm.MODE = 'SECURITY-RULES'
        form.reload()

    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE",
    )

    def delete_cb():
        try:
            val = main.GATEWAY.DeleteSecurityGroup(
                form=form, SecurityGroupId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()
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
        npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        exit()
        mainForm.MODE = 'SECURITY-RULES'
        form.reload()

    remove = F.add_widget(
        npyscreen.ButtonPress,
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
        npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        exit()
        mainForm.MODE = 'SECURITY-RULES'
        form.reload()

    remove = F.add_widget(
        npyscreen.ButtonPress,
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
    id = main.SECURITY_GROUP
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
        npyscreen.TitleCombo,
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
        res = main.GATEWAY.UpdateVm(
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
    btn_delete = F.add_widget(npyscreen.ButtonPress, name="DELETE")

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
    npyscreen.ActionPopup.DEFAULT_LINES = 15
    F = ConfirmCancelPopup(name='New Security Rule', color=form_color)

    F.preserve_selected_widget = True
    F.add_widget(npyscreen.Textfield, value="From PORT:", editable=False)
    from_port = F.add_widget(npyscreen.Textfield, value="22", editable=True)
    F.add_widget(npyscreen.Textfield, value="To PORT:", editable=False)
    to_port = F.add_widget(npyscreen.Textfield, value="22", editable=True)
    protocole = F.add(
        npyscreen.TitleSelectOne,
        max_height=4,
        value=[0, ],
        name="Protocol",
        values=["tcp", "udp", "icmp", "all"],
        scroll_exit=True,
    )
    F.add_widget(npyscreen.Textfield, value="IP:", editable=False)
    ip = F.add_widget(
        npyscreen.Textfield, value=main.IP + "/32", editable=True
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
        npyscreen.ActionPopup.DEFAULT_LINES = 12

    F.on_ok = exit
    F.edit()
    form.current_grid.h_refresh(None)
    form.current_grid.display()


def newSecurityGroup(form, form_color='STANDOUT'):
    F = ConfirmCancelPopup(name='New Security Group', color=form_color)

    F.preserve_selected_widget = True
    F.add_widget(npyscreen.Textfield, value="Name", editable=False)
    name = F.add_widget(npyscreen.Textfield, value="NewName", editable=True)

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
    F.add_widget(npyscreen.Textfield, value="Name Filter (exemple: 'Arch *'):", editable=False)
    name = F.add_widget(npyscreen.Textfield, value="*", editable=True)

    def exit():
        form.current_grid.h_refresh(None, name_filter=name.value)
        form.current_grid.display()
        F.editing = False

    F.on_ok = exit
    F.edit()
    

def editVolume(form, volume, form_color='STANDOUT'):
    type = volume[1]
    id = volume[0]
    size = volume[2]
    vm_id = volume[4]

    F = displayPopup(
        name="{} ({}), {}gib, linked to: {}".format(id, type, size, vm_id))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    edit = F.add_widget(
        npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        exit()

    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE",
    )

    def delete_cb():
        try:
            val = main.GATEWAY.DeleteVolume(VolumeId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()

    edit.whenPressed = edit_cb
    delete.whenPressed = delete_cb

    F.edit()
    form.current_grid.display()


def editSnapshot(form, snapshot, form_color='STANDOUT'):
    id = snapshot[0]
    description = snapshot[1]
    size = snapshot[2]
    volume_id = snapshot[3]

    F = displayPopup(name="{} ({}gib), volume: {}".format(id, size, volume_id))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit
    edit = F.add_widget(
        npyscreen.ButtonPress,
        name="EDIT",
    )

    def edit_cb():
        exit()
        mainForm.MODE = "SNAPSHOT-EDIT"
        form.reload()

    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE",
    )

    def delete_cb():
        try:
            val = main.GATEWAY.DeleteSnapshot(SnapshotId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()

    edit.whenPressed = edit_cb
    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.display()


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

    reg = F.add_widget(
        npyscreen.ButtonPress,
        name="REGISTERED VMs",
    )
    reg.whenPressed = instances_registered

    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE",
    )

    def delete_cb():
        val = main.GATEWAY.DeleteLoadBalancer(LoadBalancerName=name)
        form.current_grid.h_refresh(None)
        exit()

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
    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE",
    )
    read_subnet = F.add_widget(
        npyscreen.ButtonPress,
        name="READ SUBNET",
    )

    def delete_cb():
        val = main.GATEWAY.DeleteNet(NetId=name)
        form.current_grid.h_refresh(None)
        exit()

    def subnetRead():
        exit()
        mainForm.MODE = 'SUBNET'
        form.reload()

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
        npyscreen.TitleCombo,
        name="CHOOSE A ROUTE TABLE",
        values=route_tables_vals,
        value=ROUTE.get_value() if ROUTE else 0,
    )
    associate_button = F.add_widget(
        npyscreen.ButtonPress,
        name="ASSOCIATE",
    )

    def associate():
        id_route = ROUTE.get_values()[ROUTE.get_value()]
        res = main.GATEWAY.LinkRouteTable(
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
    test = F.add_widget(
        npyscreen.ButtonPress,
        name="ASSOCIATE ROUTE TABLE"
    )
    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE",
    )

    def associateRoutetable():
        associateRouteTable(form, name)
        form.current_grid.h_refresh(None)
        exit()

    def delete_cb():
        val = main.GATEWAY.DeleteSubnet(SubnetId=name)
        form.current_grid.h_refresh(None)
        exit()
    delete.whenPressed = delete_cb
    test.whenPressed = associateRoutetable
    F.edit()
    form.current_grid.display()
    form.current_grid.refresh()


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
        mlw_width = mlw.width - 1
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
    i = 0
    while waiting:
        frames = [
            "   |/\n"
            "   +\n",

            r"  \|  \n"
            "   +\n",

            "  \\ \n"
            " --+ \n",

            "    \n"
            " --+ \n"
            "  /",

            " \n"
            "   + \n"
            "  /|",

            "  \n"
            "   + \n"
            "   |\\",

            "  \n"
            "   +--\n"
            "    \\",

            "    /\n"
            "   +-- \n"
        ]
        notify(frames[i], wide=True)
        i = i + 1
        if(i >= len(frames)):
            i = 0
        curses.napms(150)
        curses.flushinp()
    thread.join()


def editKeypair(form, line, form_color='STANDOUT'):
    name = line[0]
    fingerprint = line[1]

    F = displayPopup(name="Keypair: {}".format(name))
    F.preserve_selected_widget = True

    def exit():
        F.editing = False

    F.on_ok = exit

    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE",
    )

    def delete_cb():
        delete = npyscreen.notify_ok_cancel(
            "You will delete permanently the keypair named " + name, "Warning")
        if delete:
            try:
                val = main.GATEWAY.DeleteKeypair(form=form, KeypairName=name)
            except BaseException:
                raise
            form.current_grid.h_refresh(None)
            exit()

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

    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE",
    )

    def delete_cb():
        try:
            val = main.GATEWAY.DeleteImage(ImageId=id)
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

    edit = F.add_widget(
        npyscreen.ButtonPress,
        name="EDIT"
    )
    
    delete = F.add_widget(
        npyscreen.ButtonPress,
        name="DELETE"
    )

    def edit_cb():
        form.current_grid.h_refresh(None)
        exit()
        editRouteTable(form, id) 

    def delete_cb():
        try:
            val = main.GATEWAY.DeleteNetAccessPoint(NetAccessPointId=id)
        except BaseException:
            raise
        form.current_grid.h_refresh(None)
        exit()

    edit.whenPressed = edit_cb 
    delete.whenPressed = delete_cb
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
            npyscreen.notify_confirm("Nothing as changed")
        else:
            res = main.GATEWAY.UpdateNetAccessPoint(
                NetAccessPointId=id,
                AddRouteTableIds=added_route,
                RemoveRouteTableIds=deleted_route
            )

            if "Error" in res:
                npyscreen.notify_confirm(str(res["Errors"]))
            else:
                npyscreen.notify_confirm(
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
        npyscreen.TitleMultiSelect,
        name="SELECT ROUTE TABLE(S)",
        value=selected_routes,
        values=all_route_tables,
        max_height=4,
        scroll_exit=True
    )
    F.edit()
    form.current_grid.display()
    
    
def showHelp(arg):
    F = displayPopup(name = "Help")
    F.preserve_selected_widget = True

    ft = F.add_widget(
        npyscreen.Pager,
        )
    ft.values = [
        "Return to profile : q",
        "Exit              : Ctrl+Q",
        "Refresh           : F5 or r",
        "Help              : h\n",
    ]
    
    def ok():
        exit()

    F.on_ok = ok
    F.edit()
