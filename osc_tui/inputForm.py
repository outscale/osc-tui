import oscscreen
import main

QUESTION = 'Please, say something :)'
DEFAULT_ANSWER = ''
PREVIOUS_FORM = None


def ask(form, question=None, default_answer=None, cb=None):
    global QUESTION
    global DEFAULT_ANSWER
    global PREVIOUS_FORM
    global CB
    CB = cb
    PREVIOUS_FORM = form
    QUESTION = question if question else QUESTION
    DEFAULT_ANSWER = default_answer if default_answer else DEFAULT_ANSWER
    form.parentApp.registerForm("InputForm", InputForm())
    form.parentApp.switchForm('InputForm')


class InputForm(oscscreen.ActionFormV2):
    def create(self):
        self.how_exited_handers[oscscreen.wgwidget.EXITED_ESCAPE] = main.exit
        self.add_widget(oscscreen.Textfield, value=QUESTION,
                        editable=False)
        self.input = self.add_widget(oscscreen.Textfield, value=DEFAULT_ANSWER,
                                     editable=True)

    def on_cancel(self):
        self.parentApp.switchFormPrevious()

    def on_ok(self):
        global CB
        if CB:
            CB(self.input.value)
        self.parentApp.switchFormPrevious()


if __name__ == '__main__':
    class MyTestApp(oscscreen.NPSAppManaged):
        def onStart(self):
            self.registerForm("MAIN", InputForm())
    MyTestApp().run()
