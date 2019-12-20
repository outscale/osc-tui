import npyscreen
import main

IMG = None

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
        IMG = None

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
            if IMG == None:
                self.add_widget(npyscreen.TitleText,
                                name="Argument Missing:",
                                value="Need an Image" + img_list.display_value(img_list.values[img_list.value]))
                self.display()
                return
            main.GATEWAY.CreateVms(ImageId=img)

        imgs = main.GATEWAY.ReadImages()["Images"]
        imgs_vals = []
        for img in imgs:
            account = img["AccountAlias"] if "AccountAlias" in img else "Unknow User"
            imgs_vals.append("creator: " + account + " id: " + img["ImageId"] + " name: " + img["ImageName"])

        img_list = self.add_widget(npyscreen.TitleCombo, name="CHOOSE IMG", values=imgs_vals)
        self.add_widget(npyscreen.ButtonPress, name="CREATE").whenPressed = creat
        self.add_widget(npyscreen.ButtonPress, name="EXIT").whenPressed = back
