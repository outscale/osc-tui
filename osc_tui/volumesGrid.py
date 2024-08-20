import osc_npyscreen

from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class VolumeGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = [
            "Id",
            "Type",
            "State",
            'Size (Gb)',
            'Subregion',
            'Linked To',
            "Device Name",
            'iops']

        def on_selection(line):
            popup.editVolume(self.form, line)

        self.on_selection = on_selection

    def custom_print_cell(self, cell, cell_value):
        # Checking if we are in the table and not in the title's row.
        if not isinstance(cell.grid_current_value_index, int):
            y, _ = cell.grid_current_value_index
            linkto = self.values[y][5]
            cell.highlight_whole_widget = True
            if linkto == "Unlinked":
                cell.color = "CURSOR"
            else:
                cell.color = "GOODHL"


    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadVolumes(form=self.form)
        if groups is None:
            return None
        return groups['Volumes']

    def refresh(self):
        groups = main.do_search(self.data.copy(), ['VolumeId', 'VolumeType', 'State',
                                                   'Size', 'SubregionName', 'Iops'])
        values = list()
        for g in groups:
            VolLink = g["LinkedVolumes"]
            VmId = VolLink[0]["VmId"] if VolLink else "Unlinked"
            DName = VolLink[0]["DeviceName"] if VolLink else "No Dev Today"
            values.append([g["VolumeId"], g["VolumeType"], g["State"],
                           g["Size"], g['SubregionName'], VmId, DName, g['Iops'] if 'Iops' in g else '??'])
        self.values = values


class VolumeLink(osc_npyscreen.FormBaseNew):
    LIST_THRESHOLD=4
    volume=None
    def __init__(self, *args, **keywords):
        self.volume = keywords["volume"]
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("Volume-Link", CreateVolume, name="osc-tui")
        self.parentApp.switchForm("Volume-Link")

    def back(self):
        main.kill_threads()
        self.parentApp.switchForm("Cockpit")

    def update(self):
        id=self.volume[0]
        main.GATEWAY.LinkVolume(VolumeId=id,
                                VmId=self.link_to_wid.get_values()[self.link_to_wid.get_value()][0],
                                DeviceName="/dev/" + self.alias_wid.get_value())
        self.back()

    def create(self):
        vms = main.readVms()
        vms_lst = []
        for vm in vms:
            name = vm["Tags"][0]["Value"] if len(vm["Tags"]) else "(a Vm with no Name)"
            vms_lst.append([vm["VmId"], name])

        self.alias_wid = self.add_widget(
            osc_npyscreen.TitleText,
            name="Alias(xvdX):",
            relx=self.LIST_THRESHOLD,
            value="xvd")

        self.link_to_wid = self.add_widget(
            osc_npyscreen.TitleCombo,
            relx=self.LIST_THRESHOLD,
            name="target vm",
            value=0,
            values=vms_lst
        )

        self.add_widget(osc_npyscreen.ButtonPress,
                        name="LINK").whenPressed = self.update
        self.add_widget(osc_npyscreen.ButtonPress,
                        name="EXIT").whenPressed = self.back

class VolumeEdit(osc_npyscreen.FormBaseNew):
    volume=None
    size=10
    size_wid=None
    iops=None
    LIST_THRESHOLD=4

    def __init__(self, *args, **keywords):
        self.volume = keywords["volume"]
        self.size = self.volume[2]
        self.iops = self.volume[6]
        self.type = self.volume[1]
        super().__init__(*args, **keywords)

    def reload(self):
        main.kill_threads()
        self.parentApp.addForm("Volume-Edit", CreateVolume, name="osc-tui")
        self.parentApp.switchForm("Volume-Edit")

    def back(self):
        main.kill_threads()
        self.parentApp.switchForm("Cockpit")

    def update(self):
        id=self.volume[0]
        iops_dst = self.iops_wid.get_value() if self.iops != self.iops_wid.get_value() else None
        t = self.type_wid.get_values()[self.type_wid.get_value()]
        if iops_dst:
            if iops_dst.isnumeric() == False or t == 'standard':
                iops_dst = None
            else:
                iops_dst = int(iops_dst)
        main.GATEWAY.UpdateVolume(VolumeId=id,
                                  VolumeType=t,
                                  Size=int(self.size_wid.get_value()), Iops=iops_dst)
        self.back()

    def create(self):

        self.size_wid = self.add_widget(
            osc_npyscreen.TitleText,
            relx=self.LIST_THRESHOLD,
            name="size",
            value=str(self.size)
        )

        self.iops_wid = self.add_widget(
            osc_npyscreen.TitleText,
            relx=self.LIST_THRESHOLD,
            name="iops",
            value=str(self.iops)
        )

        tval = None
        i = 0
        type_values = ['standard', 'gp2', 'io1']
        for t in type_values:
            if t == self.type:
                tval = i
            i += 1

        self.type_wid = self.add_widget(
            osc_npyscreen.TitleCombo,
            relx=self.LIST_THRESHOLD,
            name="type",
            value=tval,
            values=type_values
        )

        self.add_widget(osc_npyscreen.ButtonPress,
                        name="UPDATE").whenPressed = self.update
        self.add_widget(osc_npyscreen.ButtonPress,
                        name="EXIT").whenPressed = self.back



class VolumeGridForOneInstance(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["ID", "Name", 'Size (Gb)', 'Subregion']

        def on_selection(line):
            pass

        self.on_selection = on_selection

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadVolumes(
            form=self.form, Filters={
                'LinkVolumeVmIds': [id]})
        if groups is None:
            return None
        return groups['Volumes']


    def refresh(self):
        groups = main.do_search(self.data.copy(), ['VolumeId', 'VolumeType',
                                                   'Size', 'SubregionName'])
        values = list()
        for g in groups:
            values.append([g["VolumeId"], g["VolumeType"],
                           g["Size"], g['SubregionName']])
        self.values = values
