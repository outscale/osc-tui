import osc_npyscreen
from osc_tui import main
from osc_tui import preloader

# NAME input.
NAME = None
# SUBREGION name
SUBREGION = None
# The routing protocol
PROTOCOL = None
# he port on which the load balancer is listening
BACKENDPORT = None
# The port on which the load balancer is listening
LOADBALANCERPORT = None


class CreateLoadbalancer(osc_npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm(
            "CREATE_LOADBALANCER",
            CreateSnapshot,
            name="osc-tui")
        self.parentApp.switchForm("CREATE_LOADBALANCER")

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create():
            name = NAME.get_value()
            protocol = PROTOCOL.get_values()[PROTOCOL.get_value()]
            main.GATEWAY.CreateLoadBalancer(
                form=self,
                SubregionNames=[SUBREGION.get_values()[SUBREGION.get_value()]],
                Listeners=[{
                    "BackendPort": int(BACKENDPORT.get_value()),
                    "LoadBalancerPort": int(LOADBALANCERPORT.get_value()),
                    "LoadBalancerProtocol": protocol
                }],
                LoadBalancerName=name,
            )
            back()

        global NAME
        NAME = self.add_widget(
            osc_npyscreen.TitleText,
            name="loadbalancer's name:",
            value=NAME.get_value() if NAME else ""
        )
        global SUBREGION
        subregions = preloader.Preloader.get('subregions')
        subregions_vals = []
        for subregion in subregions:
            subregions_vals.append(subregion["SubregionName"])
        SUBREGION = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="CHOOSE A SUBREGION",
            values=subregions_vals,
            value=SUBREGION.get_value() if SUBREGION else 0
        )
        global PROTOCOL
        protocol_value = "HTTP HTTPS TCP SSL UDP".split(" ")
        PROTOCOL = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="CHOOSE A LOAD BALANCER PROTOCOL",
            values=protocol_value,
            value=PROTOCOL.get_value() if PROTOCOL else 0
        )
        global BACKENDPORT
        BACKENDPORT = self.add_widget(
            osc_npyscreen.TitleText,
            name="CHOOSE THE BACKEND PORT (between 1 and 65535)",
            value=BACKENDPORT.get_value() if BACKENDPORT else "1"
        )
        global LOADBALANCERPORT
        LOADBALANCERPORT = self.add_widget(
            osc_npyscreen.TitleText,
            name="CHOOSE THE LOADBALANCER PORT (between 1 and 65535)",
            value=LOADBALANCERPORT.get_value() if LOADBALANCERPORT else "1"
        )
        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="CREATE"
        ).whenPressed = create
        self.add_widget(osc_npyscreen.ButtonPress, name="EXIT").whenPressed = back
