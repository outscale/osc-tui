from osc_tui import main
from osc_tui import popup
from osc_tui import selectableGrid

class userGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "Name", "email", "CreationDate"]

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadUsers(form=self.form)['Users']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["UserId", "UserName",
                                                   "UserEmail", "CreationDate"])
        values = list()
        for g in groups:
            values.append([g['UserId'], g['UserName'], g['UserEmail'],
                           g["CreationDate"]])
        self.values = values

class userGroupGrid(selectableGrid.SelectableGrid):
    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, *args, **keywords)
        self.col_titles = ["Id", "Name", "Path", "Orn", "CreationDate"]

    def refresh_call(self, name_filter=None):
        groups = main.GATEWAY.ReadUserGroups(form=self.form)['UserGroups']
        return groups

    def refresh(self):
        groups = main.do_search(self.data.copy(), ["UserGroupId", "Name",
                                                   "Path", "Orn", "CreationDate"])
        values = list()
        for g in groups:
            values.append([g['UserGroupId'], g['Name'], g['Path'], g["Orn"],
                           g["CreationDate"]])
        self.values = values
