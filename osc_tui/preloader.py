import threading
import main
import popup

class Preloader():
    data = dict()
    def init():
        Preloader.register(lambda : main.GATEWAY.ReadSubregions()["Subregions"], 'subregions')
        Preloader.register(lambda : main.GATEWAY.ReadImages()["Images"], 'vm_images')
        Preloader.register(lambda : main.GATEWAY.ReadVmTypes()["VmTypes"], 'vm_types')
    def load(name = None):
        if name:
            Preloader.data.get(name).load()
        else:
            for key in Preloader.data:
                Preloader.data.get(key).load()
    def get(name):
        return Preloader.data[name].value
    def load_async(name = None):
        Preloader.loaded = False
        def cb():
            Preloader.load(name)
            Preloader.loaded = True
        threading.Thread(target=cb).start()

    def register(fct, name):
        class loader():
            def __init__(self, fct, name):
                self.fct = fct
                self.value = None
            def load(self):
                self.value = self.fct()
        Preloader.data.update({name : loader(fct, name)})

    def wait_for_preload(form):
        def cb():
            while(Preloader.loaded == False):
                pass
        popup.startLoading(form, cb)