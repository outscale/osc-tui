import sys

import npyscreen
import pyperclip

import main
import securityForm
import securityRulesForm

inspector = None


def add_security_inspector(form):
    a = form.add_widget(npyscreen.Textfield, rely=form.draw_line_at + 2, value="No security group selected",
                        editable=False)
    edit = form.add_widget(npyscreen.ButtonPress, name="EDIT")
    new = form.add_widget(npyscreen.ButtonPress, name="NEW")
    delete = form.add_widget(npyscreen.ButtonPress, name="DELETE")
    quit = form.add_widget(npyscreen.ButtonPress, name="EXIT")

    def stop():
        main.kill_threads()
        form.parentApp.switchForm('Cockpit')
    form.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = stop
    quit.whenPressed = stop
    i = Inspector(form, a, edit)
    return i


class Inspector():
    def __init__(self, form, name_label, edit):
        self.form = form
        self.name_label = name_label
        self.edit = edit

    def set_value(self, value):
        self.name_label.value = 'Selected group: ' + value[1]
        main.SECURITYGROUP = value[0]

        def edit():
            main.kill_threads()
            self.form.parentApp.addForm(
                "SecurityRules", securityRulesForm.SecurityRulesForm, name="osc-cli-curses")
            self.form.parentApp.switchForm('SecurityRules')
        self.edit.whenPressed = edit
