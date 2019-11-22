import sys

import npyscreen
import pyperclip

import main
import securityRulesForm
import inputForm

inspector = None


def add_security_inspector(form):
    a = form.add_widget(npyscreen.Textfield, rely=form.draw_line_at + 2, value="No security group selected",
                        editable=False)
    edit = form.add_widget(npyscreen.ButtonPress, name="EDIT")
    new = form.add_widget(npyscreen.ButtonPress, name="ADD NEW")
    delete = form.add_widget(npyscreen.ButtonPress, name="DELETE")
    quit = form.add_widget(npyscreen.ButtonPress, name="EXIT")

    def stop():
        main.kill_threads()
        form.parentApp.switchForm('Cockpit')
    form.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = stop
    quit.whenPressed = stop
    i = Inspector(form, a, edit, new)
    return i


class Inspector():
    def __init__(self, form, name_label, edit, new):
        self.form = form
        self.name_label = name_label
        self.edit = edit
        self.new = new

    def set_value(self, value):
        self.name_label.value = 'Selected group: ' + value[1]

        def edit():
            main.kill_threads()
            self.form.parentApp.addForm(
                "SecurityRules", securityRulesForm.SecurityRulesForm, name="osc-cli-curses")
            self.form.parentApp.switchForm('SecurityRules')
        def new():
            def create_sg(name):
                pass
            inputForm.ask(self.form, 'Enter the new security group\'s name:', '', create_sg)
        self.edit.whenPressed = edit
        self.new.whenPressed = new
