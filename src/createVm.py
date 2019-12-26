import npyscreen
import main

TITLE_COMBO = None
ID_LIST = None

class ChooseImg(npyscreen. FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
    def create(self):
        def back():
            self.parentApp.switchForm('CREATE_VM')
        self.add_widget(npyscreen.ButtonPress, name="EXIT").whenPressed = back

class CreateVm(npyscreen. FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):

        def back():
            main.kill_threads()
            self.parentApp.switchForm('Cockpit')
        self.inspector = None

        def choose_img():
            main.kill_threads()
            self.parentApp.addForm(
                "CHOOSE_IMG", ChooseImg, name="osc-cli-curses"
            )
            self.parentApp.switchForm("CHOOSE_IMG")

        def creat():
            if TITLE_COMBO.get_value == None:
                npyscreen.notify_wait('No image selected, please select one.',
                    title="Argument Missing",
                    form_color='STANDOUT',
                    wrap=True,
                    wide=False)
                self.display()
                return
            else:
                ID = ID_LIST[TITLE_COMBO.get_value()]
                npyscreen.notify_wait(str(main.GATEWAY.CreateVms(ImageId=ID)))

        imgs = main.GATEWAY.ReadImages()["Images"]
        imgs_vals = []
        ID_LIST = []
        for img in imgs:
            account = img["AccountAlias"] if "AccountAlias" in img else "Unknow User"
            imgs_vals.append("creator: " + account + " id: " + img["ImageId"] + " name: " + img["ImageName"])
            ID_LIST.append(img["ImageId"])

        TITLE_COMBO = self.add_widget(npyscreen.TitleCombo, name="CHOOSE IMG", values=imgs_vals)
        self.add_widget(npyscreen.ButtonPress, name="CREATE").whenPressed = creat
        self.add_widget(npyscreen.ButtonPress, name="EXIT").whenPressed = back
