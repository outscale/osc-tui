import sys

import npyscreen
import pyperclip

import main
import securityForm

inspector = None


def add_security_inspector(form):
    a = form.add_widget(npyscreen.Textfield, rely = form.draw_line_at + 2, value="No security group selected",
                        editable=False)
    edit = form.add_widget(npyscreen.ButtonPress, name="EDIT")
    quit = form.add_widget(npyscreen.ButtonPress, name="EXIT")

    def stop():
        main.kill_threads()
        form.parentApp.switchForm('Cockpit')
    quit.whenPressed = stop
    i = Inspector(form, a)
    return i


class Inspector():
    def __init__(self, form, name_label):
        self.form = form
        self.name_label = name_label
        pass
    def set_value(self, value):
        self.name_label.value = 'Selected group: ' + value[1]

