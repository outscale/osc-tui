
import main
import mainForm
import npyscreen
import npyscreen.fmPopup
import npyscreen.wgmultiline
import pyperclip
import securityGroupsGrid
import securityRulesGrid


class ConfirmCancelPopup(npyscreen.fmPopup.ActionPopup):
    def on_ok(self):
        self.value = True

    def on_cancel(self):
        self.value = False


class displayPopup(npyscreen.fmPopup.Popup):
    def on_ok(self):
        self.editing = False
        self.value = True


def readString(form_color='STANDOUT'):

    F = ConfirmCancelPopup(name='', color=form_color)
    F.preserve_selected_widget = True
    tf = F.add(npyscreen.Textfield)
    tf.width = tf.width - 1
    tf.value = default_value
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
        region = F.add_widget(
            npyscreen.TitleCombo,
            name="REGION:",
            values="eu-west-2 eu-west-1".split(),
            value=0,
        )
        #ak.width = ak.width - 1
        F.edit()
        if F.value is True:
            if name.value != '' and ak.value != '' and sk.value != '':
                return {
                    name.value: {
                        'access_key': ak.value,
                        'secret-key': sk.value,
                        'region': region.values[region.value]
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
        form.current_grid.refresh()
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
        main.GATEWAY.StartVms(VmIds=[id])
        exit()

    def terminate_vm():
        main.kill_threads()
        if npyscreen.notify_ok_cancel(
                "Do you really want to terminate this vm:\nName: " + name +
                "\nID: " + id,
                "VM Termination",
        ):
            main.GATEWAY.DeleteVms(VmIds=[id])
        exit()

    def stop_vm():
        main.GATEWAY.StopVms(VmIds=[id])
        exit()

    def force_stop_vm():
        main.GATEWAY.StopVms(ForceStop=True, VmIds=[id])
        exit()

    def restart_vm():
        main.GATEWAY.RebootVms(VmIds=[id])
        exit()

    def sg():
        exit()
        main.kill_threads()
        main.VM = main.VMs[id]
        mainForm.CURRENT_GRID_CLASS = securityGroupsGrid.SecurityGroupsGridForOneInstance
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

    copy_ip.whenPressed = copy_ip
    run_stop.whenPressed = start_vm if status == "stopped" else stop_vm
    force_stop.whenPressed = force_stop_vm
    restart.whenPressed = restart_vm
    security.whenPressed = sg
    terminate.whenPressed = terminate_vm
    copy_ip.whenPressed = _copy_ip
    volumes.whenPressed = volumes_cb
    F.edit()


def editSecurityGroup(form, sg, form_color='STANDOUT'):
    name = sg[1]
    id = sg[0]
    main.SECURITY_GROUP = id
    F = displayPopup(name=name + ' (' + id + ')', color=form_color)
    F.preserve_selected_widget = True

    def exit():
        form.current_grid.refresh()
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
            val = main.GATEWAY.DeleteSecurityGroup(SecurityGroupId=id)
        except BaseException:
            raise
        exit()
    edit.whenPressed = edit_cb
    delete.whenPressed = delete_cb
    F.edit()
    form.current_grid.refresh()
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
        main.GATEWAY.UpdateVm(VmId=main.VM["VmId"], SecurityGroupIds=values)
        exit()
    edit.whenPressed = edit_cb
    remove.whenPressed = remove_cb
    F.edit()
    form.current_grid.refresh()
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
        exit()

    btn_delete.whenPressed = delete
    F.edit()
    form.current_grid.ensure_cursor_on_display_down_right(None)
    form.current_grid.ensure_cursor_on_display_up(None)
    form.current_grid.refresh()
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
    form.current_grid.refresh()
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
    form.current_grid.refresh()
    form.current_grid.display()
