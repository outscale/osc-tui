import threading
from osc_tui import main
from osc_tui import popup

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

    def free(form):
        Preloader.wait_for_preload(form)
        Preloader.data = dict()

    # If no name given, we preload all registered datas!
    # If name is list we update for each name.
    # Else we update only the selected name.

    def load(name=None):
        if isinstance(name, list):
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
        Preloader.loading += 1

        def cb():
            # Prevent too many api calls at a time.
            while(Preloader.loading > 3):
                pass
            Preloader.load(name)
            Preloader.loading -= 1
        threading.Thread(target=cb).start()

    def load_in_parallel(ls=None):
        if isinstance(ls, list):
            for key in ls:
                Preloader.load_async(key)
        else:
            for key in Preloader.data:
                Preloader.load_async(key)

    def register(fct, name):
        class loader():
            def __init__(self, fct, name):
                self.fct = fct
                self.value = None
                self.loading = False
                self.name = name

            def load(self):
                self.loading = True
                self.value = self.fct()
                self.loading = False

        Preloader.data.update({name: loader(fct, name)})

    # Can wait for the preload of everything or the preload of ['smthg',
    # 'smthg1'] or of 'smthg'.
    def wait_for_preload(form, name=None):
        def cb():
            if name is None:
                while(Preloader.loading > 0):
                    pass
            elif isinstance(name, dict):
                for key in name:
                    while(Preloader.get(key).loading):
                        pass
            else:
                while(Preloader.get(name).loading):
                    pass

        # Avoid starting the animation if no need.

        if Preloader.loading > 0:
            popup.startLoading(form, cb)
