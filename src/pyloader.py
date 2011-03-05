
import core.cmdman

class PyLoader:
    def __init__(self):
        pass

    @staticmethod
    def _get_python_module(module_name):
        # TODO: more error checking?
        mod = __import__(module_name, globals(), locals(), [], 0)
        mod_list = module_name.split('.')
        for submod in mod_list[1:]:
            mod = mod.__dict__[submod]
        return mod

    def get_component_class(self, component_name):
        module = self._get_python_module(component_name)
        main_class = None
        for value in module.__dict__.values():
            try:
                component_info = value.component_info
                assert(main_class == None) # only want one per file
                main_class = value
            except AttributeError:
                pass
        assert(main_class != None)
        return main_class
