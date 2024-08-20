import osc_npyscreen

from osc_tui import main

# Textbox for name input
NAME = None
# All vpcs combo box.
VPC_COMBO = None
# All service combo box.
SERVICE_COMBO = None
# Multiline selection
ROUTES_MULTISELECT = None

class CreateNetAccessPoint(osc_npyscreen.FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm(
            "CREATE_NET-ACCESS-POINT",
            CreateNetAccessPoint,
            name="osc-tui"
            )
        self.parentApp.switchForm("CREATE_NET-ACCESS-POINT")


    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm("Cockpit")

        self.inspector = None

        def create():
            if (not ROUTES_MULTISELECT.get_value()
                or VPC_COMBO.get_value() is None
                or SERVICE_COMBO.get_value() is None):
                osc_npyscreen.notify_confirm(
                    "No vcp/service or routes selected, please select one.",
                    title="Argument Missing",
                    form_color="STANDOUT",
                    wrap=True,
                    wide=False
                )
                self.display()
                return
            else:
                vpc = VPC_COMBO.get_values()[
                    VPC_COMBO.get_value()
                ]
                service = SERVICE_COMBO.get_values()[
                    SERVICE_COMBO.get_value()
                ]
                route_tables = [
                    ROUTES_MULTISELECT.get_values()[i]
                    for i in ROUTES_MULTISELECT.get_value()
                ]
                res = main.GATEWAY.CreateNetAccessPoint(
                    form=self,
                    NetId=vpc,
                    RouteTableIds=route_tables,
                    ServiceName=service
                )
                if "Errors" in res:
                    osc_npyscreen.notify_confirm(str(res["Errors"]))
                back()
                

        vpcs = main.GATEWAY.ReadNets(form=self)['Nets']
        vpcs_vals = []
        for g in vpcs:
            vpcs_vals.append(g['NetId'])

        services = main.GATEWAY.ReadNetAccessPointServices(form=self)['Services']
        services_vals = []
        for s in services:
            services_vals.append(s['ServiceName'])

        routes = main.GATEWAY.ReadRouteTables(form=self)['RouteTables']
        routes_vals = []
        for r in routes:
            routes_vals.append(r['RouteTableId'])
        
        global VPC_COMBO
        VPC_COMBO = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="CHOOSE A VPC",
            values=vpcs_vals,
            value=VPC_COMBO.get_value() if VPC_COMBO else 0
        )
        global SERVICE_COMBO
        SERVICE_COMBO = self.add_widget(
            osc_npyscreen.TitleCombo,
            name="CHOOSE A SERVICE",
            values=services_vals,
            value=SERVICE_COMBO.get_value() if SERVICE_COMBO else 0
        )
        global ROUTES_MULTISELECT
        ROUTES_MULTISELECT  = self.add_widget(
            osc_npyscreen.TitleMultiSelect,
            name="SELECT ROUTE TABLE(S)",
            values=routes_vals,
            max_height=6,
            scroll_exit=True
        )
        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="CREATE"
            ).whenPressed = create
        self.add_widget(
            osc_npyscreen.ButtonPress,
            name="EXIT"
            ).whenPressed = back
