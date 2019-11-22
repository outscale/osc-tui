import sys

import npyscreen
import pyperclip
from requests import get

import main
import securityForm
import securityRulesInspector
import securityRuleInputForm

ip = get('https://api.ipify.org').text

inspector = None


def add_security_rules_inspector(form):
    a = form.add_widget(npyscreen.Textfield, rely=form.draw_line_at + 2, value="No security rule selected",
                        editable=False)
    delete = form.add_widget(npyscreen.ButtonPress, name="DELETE")

    def new_sr():
        securityRuleInputForm.ask(inspector.form)

    def new_sr_ssh():
        main.GATEWAY.CreateSecurityGroupRule(FromPortRange = 22,
                IpProtocol= 'tcp',
                IpRange= ip + '/32',
                ToPortRange= 22,
                SecurityGroupId= main.SECURITY_GROUP,
                Flow= 'Inbound',
                )
    new = form.add_widget(npyscreen.ButtonPress, name="NEW")
    new.whenPressed = new_sr
    new_ssh_myip = form.add_widget(
        npyscreen.ButtonPress, name="NEW SSH FROM MY IP")
    new_ssh_myip.whenPressed = new_sr_ssh
    quit = form.add_widget(npyscreen.ButtonPress, name="EXIT")

    def stop():
        main.kill_threads()
        form.parentApp.switchForm('Security')
    form.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = stop
    quit.whenPressed = stop
    inspector = Inspector(form, a, delete)
    return inspector


class Inspector():
    def __init__(self, form, name_label, delete):
        self.form = form
        self.name_label = name_label
        self.delete = delete

    def set_value(self, value):
        self.protocol = value[0]
        self.from_port = value[1]
        self.to_port = value[2]
        self.ip_range = value[3]

        self.name_label.value = 'Selected rule: ' + str(value[0] + ' from: ' + str(
            value[1]) + ' to: ' + str(value[2]) + ' with ip: ' + str(value[3]))

        def delete():
            main.GATEWAY.DeleteSecurityGroupRule(FromPortRange = self.from_port,
                    IpProtocol= self.protocol,
                    IpRange= self.ip_range,
                    ToPortRange= self.to_port,
                    SecurityGroupId= main.SECURITY_GROUP,
                    Flow= 'Inbound',
                    )
        self.delete.whenPressed = delete
