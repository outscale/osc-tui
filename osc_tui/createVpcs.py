import oscscreen
import main
import popup
import os
import preloader

# CIDR input for vpcs
CIDR = None
# CIDR input for subnet
CIDRSUBNET = None
# List of all Subregions
SUBREGION = None


class createVpcs(oscscreen.FormBaseNew):
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
            oscscreen.TitleText,
            name="CIDR (for example:10.0.0.0/16)",
            value=CIDR.get_value() if CIDR else "")
        self.add_widget(
            oscscreen.ButtonPress,
            name="CREATE"
        ).whenPressed = create
        self.add_widget(oscscreen.ButtonPress, name="EXIT").whenPressed = back


class createSubnet(oscscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm(
            "CREATE_SUBNET",
            CreateSubnet,
            name="osc-tui")
        self.parentApp.switchForm("CREATE_SUBNET")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create():
            cidr = CIDRSUBNET.get_value()
            res = main.GATEWAY.CreateSubnet(
                form=self,
                IpRange=cidr,
                NetId=popup.SUBNETID,
                SubregionName=SUBREGION.get_values()[SUBREGION.get_value()],
            )
            back()

        global CIDR
        CIDRSUBNET = self.add_widget(
            oscscreen.TitleText,
            name="CIDR (for example:10.0.0.0/16)",
            value=CIDR.get_value() if CIDR else "")
        global SUBREGION
        subregions = preloader.Preloader.get('subregions')
        subregions_vals = []
        for subregion in subregions:
            subregions_vals.append(subregion["SubregionName"])
        SUBREGION = self.add_widget(
            oscscreen.TitleCombo,
            name="CHOOSE SUBREGION",
            values=subregions_vals,
            value=SUBREGION.get_value() if SUBREGION else 0,
        )
        self.add_widget(
            oscscreen.ButtonPress,
            name="CREATE"
        ).whenPressed = create
        self.add_widget(oscscreen.ButtonPress, name="EXIT").whenPressed = back
