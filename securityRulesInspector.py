import sys

import npyscreen
import pyperclip

import main
import securityForm

inspector = None


def add_security_rules_inspector(form):
    a = form.add_widget(npyscreen.Textfield, rely = form.draw_line_at + 2, value="No security rule selected",
                        editable=False)
    delete = form.add_widget(npyscreen.ButtonPress, name="DELETE")
    new = form.add_widget(npyscreen.ButtonPress, name="NEW")
    quit = form.add_widget(npyscreen.ButtonPress, name="EXIT")

    def stop():
        main.kill_threads()
        form.parentApp.switchForm('Security')
    form.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = stop
    quit.whenPressed = stop
    i = Inspector(form, a)
    return i


class Inspector():
    def __init__(self, form, name_label):
        self.form = form
        self.name_label = name_label
        pass
    def set_value(self, value):
        self.name_label.value = 'Selected rule: ' + str(value[0] + ' from: ' + str(value[1]) + ' to: ' + str(value[2]) + ' with ip: ' + str(value[3]))

