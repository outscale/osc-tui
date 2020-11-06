import npyscreen
import main
import popup
import os
import preloader

# CIDR input
CIDR = None

class createVpcs(npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm(
            "CREATE_VPCS",
            CreateVpcs,
            name="osc-tui")
        self.parentApp.switchForm("CREATE_VPCS")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create():
            cidr = CIDR.get_value()
            res = main.GATEWAY.CreateNet(
                form=self,
                IpRange=cidr,
            )
            back()

        global CIDR
        CIDR = self.add_widget(
            npyscreen.TitleText,
            name="CIDR",
            value=CIDR.get_value() if CIDR else "")
        self.add_widget(
            npyscreen.ButtonPress,
            name="CREATE"
        ).whenPressed = create
        self.add_widget(npyscreen.ButtonPress, name="EXIT").whenPressed = back
