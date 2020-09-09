import threading
import main
import popup

# The static class managing data preloading.


class Preloader():
    data = dict()
    loading = 0

    def init():
        # Here we register every data we need to preload.
        Preloader.register(lambda: main.GATEWAY.ReadSubregions()[
                           "Subregions"], 'subregions')
        Preloader.register(
            lambda: main.GATEWAY.ReadImages()["Images"],
            'vm_images')
        Preloader.register(
            lambda: main.GATEWAY.ReadVmTypes()["VmTypes"],
            'vm_types')

    # If no name given, we preload all registered datas!
    # If name is list we update for each name.
    # Else we update only the selected name.

    def load(name=None):
        if type(name) is list:
            for n in name:
                Preloader.data.get(n).load()
        elif name:
            Preloader.data.get(name).load()
        else:
            for key in Preloader.data:
                Preloader.data.get(key).load()

    def get(name):
        return Preloader.data[name].value

    def load_async(name=None):
        Preloader.loading +=1

        def cb():
            Preloader.load(name)
            Preloader.loading -= 1
        threading.Thread(target=cb).start()

    def register(fct, name):
        class loader():
            def __init__(self, fct, name):
                self.fct = fct
                self.value = None

            def load(self):
                self.value = self.fct()
        Preloader.data.update({name: loader(fct, name)})

    def wait_for_preload(form):
        def cb():
            while(Preloader.loading > 0):
                pass
        popup.startLoading(form, cb)
