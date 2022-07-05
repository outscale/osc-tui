#!/usr/bin/env python

import oscscreen


class FormObject(
        oscscreen.ActionFormV2,
        oscscreen.SplitForm,
        oscscreen.FormWithMenus):
    def create(self):
        self.show_atx = 30
        self.show_aty = 5
        self.fname = self.add(oscscreen.TitleText, name='First Name:')
        self.nextrely += 1
        self.lname = self.add(oscscreen.TitleText, name='Last Name:')

        self.menu = self.add_menu(name="Main Menu", shortcut="^M")
        self.menu.addItemsFromList([
            ("Item 1", self.press_1, "1"),
            ("Item 2", self.press_2, "2"),
            ("Exit Form", self.exit_form, "^X"),
        ])

    def press_1(self):
        oscscreen.notify_confirm("You pressed Item 1", "Item 1", editw=1)

    def press_2(self):
        oscscreen.notify_confirm("You pressed Item 2", "Item 1", editw=1)

    def exit_form(self):
        oscscreen.notify_confirm(
            "You have decided to exit the Menu", "Item 1", editw=1)
        self.parentApp.switchForm(None)

    def afterEditing(self):
        # self.parentApp.setNextForm(None)
        pass

    def on_ok(self):
        oscscreen.notify_confirm("Ok button was pressed", "Saved!!", editw=1)
        self.parentApp.setNextForm(None)

    def on_cancel(self):
        exiting = oscscreen.notify_yes_no(
            "Are you sure you want to cancel", "Positive?", editw=2)
        if exiting:
            oscscreen.notify_confirm(
                "Form has not been saved", 'bye bye', editw=1)
            self.parentApp.setNextForm(None)
        else:
            oscscreen.notify_confirm(
                "You can continue working", 'okay', editw=1)


class App(oscscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', FormObject, name='Npyscreen Test Form',
                     lines=10, columns=60, draw_line_at=7)


if __name__ == "__main__":
    app = App().run()
    # print(FormObject().fname)
