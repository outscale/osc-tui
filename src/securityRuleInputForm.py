import npyscreen

import main
import securityRulesForm

QUESTION = "Please, say something :)"
DEFAULT_ANSWER = ""
PREVIOUS_FORM = None


def ask(form, question=None, default_answer=None, cb=None):
    main.kill_threads()
    global QUESTION
    global DEFAULT_ANSWER
    global PREVIOUS_FORM
    global CB
    CB = cb
    PREVIOUS_FORM = form
    QUESTION = question if question else QUESTION
    DEFAULT_ANSWER = default_answer if default_answer else DEFAULT_ANSWER
    form.parentApp.registerForm("SecurityRuleInputForm", InputForm())
    form.parentApp.switchForm("SecurityRuleInputForm")


class InputForm(npyscreen.ActionFormV2):
    def create(self):
        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = main.exit
        self.add_widget(npyscreen.Textfield, value="From PORT:", editable=False)
        self.from_port = self.add_widget(npyscreen.Textfield, value="22", editable=True)
        self.add_widget(npyscreen.Textfield, value="To PORT:", editable=False)
        self.to_port = self.add_widget(npyscreen.Textfield, value="22", editable=True)
        self.protocole = self.add(
            npyscreen.TitleSelectOne,
            max_height=4,
            value=[0,],
            name="Protocol",
            values=["tcp", "udp", "icmp"],
            scroll_exit=True,
        )
        self.add_widget(npyscreen.Textfield, value="IP:", editable=False)
        self.ip = self.add_widget(
            npyscreen.Textfield, value=main.IP + "/32", editable=True
        )

    def on_cancel(self):
        self.parentApp.addForm(
            "SecurityRules", securityRulesForm.SecurityRulesForm, name="osc-cli-curses"
        )
        self.parentApp.switchForm("SecurityRules")

    def on_ok(self):
        main.GATEWAY.CreateSecurityGroupRule(
            FromPortRange=int(self.from_port.value),
            IpProtocol=self.protocole.get_selected_objects()[0],
            IpRange=self.ip.value,
            ToPortRange=int(self.to_port.value),
            SecurityGroupId=main.SECURITY_GROUP,
            Flow="Inbound",
        )
        self.parentApp.addForm(
            "SecurityRules", securityRulesForm.SecurityRulesForm, name="osc-cli-curses"
        )
        self.parentApp.switchForm("SecurityRules")


if __name__ == "__main__":

    class MyTestApp(npyscreen.NPSAppManaged):
        def onStart(self):
            self.registerForm("MAIN", InputForm())

    MyTestApp().run()
