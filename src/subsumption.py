import pyloader
import compman
import conf

if __name__ == '__main__':
    # create a component manager
    component_manager = compman.ComponentManager()

    # add the python loader
    component_manager.add_loader(pyloader.PyLoader())

    # read components.conf
    component_list = conf.ListConfigFile('conf/components.conf')
    component_manager.load_list(component_list)
    cmdman = component_manager.interfaces['cmdman']
    cmdman.do_command("test", "params", "p", None)