import npyscreen
import main

QUESTION = 'Please, say something :)'
DEFAULT_ANSWER = ''
PREVIOUS_FORM = None

def ask(form, question = None, default_answer = None, cb = None):
    main.kill_threads()
    global QUESTION
    global DEFAULT_ANSWER
    global PREVIOUS_FORM
    global CB
    CB = cb
    PREVIOUS_FORM = form
    QUESTION = question if question else QUESTION
    DEFAULT_ANSWER = default_answer if default_answer else DEFAULT_ANSWER
    form.parentApp.registerForm("SecurityRuleInputForm", InputForm())
    form.parentApp.switchForm('SecurityRuleInputForm')



class InputForm(npyscreen.ActionFormV2):
    def create(self):
        self.how_exited_handers[npyscreen.wgwidget.EXITED_ESCAPE] = main.exit
        self.add_widget(npyscreen.Textfield, value='From PORT:',
                        editable=False)
        self.from_port = self.add_widget(npyscreen.Textfield, value='22',
                        editable=True)
        self.add_widget(npyscreen.Textfield, value='To PORT:',
                        editable=False)
        self.to_port = self.add_widget(npyscreen.Textfield, value='22',
                        editable=True)
        ms = self.add(npyscreen.TitleSelectOne, max_height=4, value = [1,], name="Protocol",
                values = ["tcp","udp","icmp"], scroll_exit=True)

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        global CB
        if CB:
            CB(self.input.value)
        self.parentApp.switchFormPrevious()

if __name__ == '__main__':
    class MyTestApp(npyscreen.NPSAppManaged):
        def onStart(self):
            self.registerForm("MAIN", InputForm())
    MyTestApp().run()

