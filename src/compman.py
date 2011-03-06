
class Interface:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<Interface '{0}'>".format(self.name)

class ComponentManager:
    def __init__(self):
        self.components = []
        self.interfaces = {}
        self.loaders = {}
        self.func_data_handlers = {}
        self.instance_data_handlers = {}

    def add_loader(self, loader, prefix=''):
        # TODO: make this better
        assert(prefix not in self.loaders)
        self.loaders[prefix] = loader

    def remove_loader(self, loader, prefix=''):
        # TODO: make this better
        assert(prefix in self.loaders)
        assert(self.loaders[prefix] == loader)
        del self.loaders[prefix]

    def _get_component_class(self, component_name):
        # TODO: error checking
        split_name = component_name.split(' ', 1)
        if len(split_name) == 1:
            loader_name = ''
        else:
            loader_name = split_name[0]
            component_name = split_name[1]
        loader = self.loaders.get(loader_name, None)
        assert(loader is not None)
        return loader.get_component_class(component_name)

    def _load_global_instance(self, component_class):
        component_info = component_class.component_info
        
        # collect the needed interfaces
        needed_interfaces = {}
        for interface in component_info['int_comp'].get('uses_global_interface', []):
            needed_interfaces[interface] = self.interfaces[interface]
        
        # instantiate it
        instance = component_class(**needed_interfaces)
        
        # register any interfaces
        for interface in component_info['int_comp'].get('global_interface', []):
            new_interface = Interface(interface)
            self.interfaces[interface] = new_interface
            for func, name in component_info['int_func'].get('interface_function', []):
                if interface in name or None in name:
                    new_interface.__dict__[func.__name__] = func.__get__(instance)
 
        # register any func_data_handlers
        for load_func, load_name in component_info['int_func'].get('comp_func_load', []):
            unload_func = None
            for f, unload_name in component_info['int_func'].get('comp_func_unload', []):
                if load_name == unload_name:
                    unload_func = f
                    break 
            self.func_data_handlers[load_name] = (load_func.__get__(instance), unload_func.__get__(instance))

        # register any instance_data_handlers
        for load_func, load_name in component_info['int_func'].get('comp_inst_load', []):
            unload_func = None
            for f, unload_name in component_info['int_func'].get('comp_inst_unload', []):
                if load_name == unload_name:
                    unload_func = f
                    break 
            self.instance_data_handlers[load_name] = (load_func.__get__(instance), unload_func.__get__(instance))
 
        # run all the instance data through handlers
        for name, data in component_info['ext_comp'].items():
            self.instance_data_handlers[name][0](instance, data)
        
        # run all the func data through handlers
        for name, funcs in component_info['ext_func'].items():
            for func, data in funcs:
                self.func_data_handlers[name][0](instance, func.__get__(instance), data)
 
        return instance

    def load_list(self, component_list):
        # these all reference classes, not instances
        unloaded_components = []
        unloaded_interfaces = {}
        unloaded_func_data_handlers = {}
        unloaded_instance_data_handlers = {}
        interface_dependencies = {}
        func_data_handler_dependencies = {}
        instance_data_handler_dependencies = {}

        # load the classes, populate unloaded_* and load dependencies
        for component_name in component_list:
            component_name = component_name.strip()
            component_class = self._get_component_class(component_name)
            component_info = component_class.component_info
            
            # add it to unloaded_components 
            unloaded_components.append(component_class)
            
            # make sure it's a global component
            assert(component_info.get('global', False))
            
            # handle unloaded_interfaces
            for interface in component_info['int_comp'].get('global_interface', []):
                assert(interface not in unloaded_interfaces)
                assert(interface not in self.interfaces)
                unloaded_interfaces[interface] = component_class
            
            # handle unloaded_func_data_handlers
            for func, name in component_info['int_func'].get('comp_func_load', []):
                assert(name not in unloaded_func_data_handlers)
                assert(name not in self.func_data_handlers)
                unloaded_func_data_handlers[name] = component_class

            # handle unloaded_func_data_handlers
            for func, name in component_info['int_func'].get('comp_inst_load', []):
                assert(name not in unloaded_instance_data_handlers)
                assert(name not in self.instance_data_handlers)
                unloaded_instance_data_handlers[name] = component_class

            # load interface dependencies
            for interface in component_info['int_comp'].get('uses_global_interface', []):
                interface_dependencies.setdefault(component_class, []).append(interface)

            for func_data_name in component_info['ext_func']:
                func_data_handler_dependencies.setdefault(component_class, []).append(func_data_name)

            for instance_data_name in component_info['ext_comp']:
                instance_data_handler_dependencies.setdefault(component_class, []).append(instance_data_name)

        # make sure there are no missing dependencies
        for interfaces in interface_dependencies.values():
            for interface in interfaces:
                assert(interface in unloaded_interfaces)
        for names in func_data_handler_dependencies.values():
            for name in names:
                assert(name in unloaded_func_data_handlers)
        for names in instance_data_handler_dependencies.values():
            for name in names:
                assert(name in unloaded_instance_data_handlers)

        # iteratively load components without dependencies
        keep_going = True
        while (keep_going):
            keep_going = False
            for component_class in unloaded_components[:]:
                if interface_dependencies.get(component_class, []):
                    continue
                if func_data_handler_dependencies.get(component_class, []):
                    continue
                if instance_data_handler_dependencies.get(component_class, []):
                    continue
                # no dependencies: load it
                self._load_global_instance(component_class)
                component_info = component_class.component_info
                
                unloaded_components.remove(component_class)
                
                # remove interface dependencies
                for interface in component_info['int_comp'].get('global_interface', []):
                    del unloaded_interfaces[interface]
                    for interfaces in interface_dependencies.values():
                        while interface in interfaces:
                            interfaces.remove(interface)
            
                # remove func_data_handler dependencies
                for func, name in component_info['int_func'].get('comp_func_load', []):
                    del unloaded_func_data_handlers[name]
                    for names in func_data_handler_dependencies.values():
                        while name in names:
                            names.remove(name)

                # remove instance_data_handler dependencies
                for func, name in component_info['int_func'].get('comp_inst_load', []):
                    del unloaded_instance_data_handlers[name]
                    for names in instance_data_handler_dependencies.values():
                        while name in names:
                            names.remove(name)

                # keep iterating while changes are happening
                keep_going = True
        
        if unloaded_components:
            raise Exception('could not resolve dependencies')

        # populate dependencies
        
            
            
