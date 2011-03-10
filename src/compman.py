import zone
import zoneutil

class ComponentLoadException(Exception):
    pass

class Interface:
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<Interface '{0}'>".format(self.name)

class ComponentManager:
    def __init__(self):
        self.loaders = {}

        self.interfaces = zoneutil.ZoneMapping()
        self.func_data_handlers = zoneutil.ZoneMapping()
        self.instance_data_handlers = zoneutil.ZoneMapping()

        self.components = {}

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
        if not loader:
            raise ComponentLoadException("No loader for '{}' found for component '{}'.".format(loader_name, component_name))
        return loader.get_component_class(component_name)

    def _load_component_class(self, component_class, scope):
        component_info = component_class.component_info

        # collect needed interfaces
        needed_interfaces = {}
        for interface_name in component_info['int_comp'].get('uses_interface', []):
            needed_interfaces[interface_name] = self.interfaces[scope][interface_name]

        # instantiate it
        instance = component_class(**needed_interfaces)

        # register any interfaces
        for interface_name in component_info['int_comp'].get('interface', []):
            new_interface = Interface(interface_name)
            self.interfaces[scope][interface_name] = new_interface
            for func, name in component_info['int_func'].get('interface_function', []):
                if interface_name in name or None in name:
                    new_interface.__dict__[func.__name__] = func.__get__(instance)

        # register any func_data_handlers
        for load_func, load_name in component_info['int_func'].get('comp_func_load', []):
            unload_func = None
            for f, unload_name in component_info['int_func'].get('comp_func_unload', []):
                if load_name == unload_name:
                    unload_func = f
                    break
            self.func_data_handlers[scope][load_name] = (load_func.__get__(instance), unload_func.__get__(instance))

        # register any instance_data_handlers
        for load_func, load_name in component_info['int_func'].get('comp_inst_load', []):
            unload_func = None
            for f, unload_name in component_info['int_func'].get('comp_inst_unload', []):
                if load_name == unload_name:
                    unload_func = f
                    break
            self.instance_data_handlers[scope][load_name] = (load_func.__get__(instance), unload_func.__get__(instance))
 
        # run all the instance data through handlers
        for name, data in component_info['ext_comp'].items():
            self.instance_data_handlers[scope][name][0](instance, data)

        # run all the func data through handlers
        for name, funcs in component_info['ext_func'].items():
            for func, data in funcs:
                self.func_data_handlers[scope][name][0](instance, func.__get__(instance), data)
 
        # TODO: remove this line
        print("loaded {} {}".format(component_class, scope))
 
        return instance

    def load_list(self, component_list, scope):
        if isinstance(scope, zone.Game):
            scope_name = "game"
        elif isinstance(scope, zone.Arena):
            scope_name = "arena"
        elif isinstance(scope, zone.Realm):
            scope_name = "realm"
        elif isinstance(scope, zone.Zone) or scope is None:
            scope_name = "zone"
        else:
            raise ComponentLoadException("Bad scope type.")
        
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

            # make sure it's a component for the right scope
            if not component_info.get(scope_name, False):
                raise ComponentLoadException("Component '{}' loading to wrong scope '{}'.".format(component_name, scope_name))

            # handle unloaded_interfaces
            for interface in component_info['int_comp'].get('interface', []):
                if interface in unloaded_interfaces:
                    raise ComponentLoadException("Attempting to load multiple '{}' interfaces to the same scope.".format(interface))
                if interface in self.interfaces[scope]:
                    raise ComponentLoadException("Attempting to load another '{}' interface to the same scope.".format(interface))
                unloaded_interfaces[interface] = component_class
            
            # handle unloaded_func_data_handlers
            for func, name in component_info['int_func'].get('comp_func_load', []):
                unloaded_func_data_handlers.setdefault(name, []).append(component_class)

            # handle unloaded_func_data_handlers
            for func, name in component_info['int_func'].get('comp_inst_load', []):
                unloaded_instance_data_handlers.setdefault(name, []).append(component_class)

            # load interface dependencies
            for interface in component_info['int_comp'].get('uses_interface', []):
                interface_dependencies.setdefault(component_class, []).append(interface)

            for func_data_name in component_info['ext_func']:
                func_data_handler_dependencies.setdefault(component_class, []).append(func_data_name)

            for instance_data_name in component_info['ext_comp']:
                instance_data_handler_dependencies.setdefault(component_class, []).append(instance_data_name)

        # make sure there are no missing dependencies
        for interfaces in interface_dependencies.values():
            for interface in interfaces:
                if interface not in self.interfaces[scope]:
                    if interface not in unloaded_interfaces:
                        raise ComponentLoadException("Could not find interface '{}'".format(interface))
        for names in func_data_handler_dependencies.values():
            for name in names:
                if name not in self.func_data_handlers[scope]:
                    if name not in unloaded_func_data_handlers:
                        raise ComponentLoadException("Could not find function data handler for '{}'".format(interface))
        for names in instance_data_handler_dependencies.values():
            for name in names:
                if name not in self.instance_data_handlers[scope]:
                    if name not in unloaded_instance_data_handlers:
                        raise ComponentLoadException("Could not find instance data handler for '{}'".format(interface))

        # iteratively load components without dependencies
        keep_going = True
        while (keep_going):
            keep_going = False
            for component_class in unloaded_components[:]:
                if interface_dependencies.get(component_class, []):
                    print("{} has interface deps".format(component_class))
                    continue
                if func_data_handler_dependencies.get(component_class, []):
                    print("{} has func data handler deps".format(component_class))
                    continue
                if instance_data_handler_dependencies.get(component_class, []):
                    print("{} has instance data handler deps".format(component_class))
                    continue
                # no dependencies: load it
                self._load_component_class(component_class, scope)
                component_info = component_class.component_info

                unloaded_components.remove(component_class)

                # remove interface dependencies
                for interface in component_info['int_comp'].get('interface', []):
                    del unloaded_interfaces[interface]
                    for interfaces in interface_dependencies.values():
                        while interface in interfaces:
                            interfaces.remove(interface)

                # remove func_data_handler dependencies
                for func, name in component_info['int_func'].get('comp_func_load', []):
                    func_data_handler_list = unloaded_func_data_handlers[name]
                    func_data_handler_list.remove(component_class)
                    if not func_data_handler_list:
                        del unloaded_func_data_handlers[name]
                        for names in func_data_handler_dependencies.values():
                            while name in names:
                                names.remove(name)

                # remove instance_data_handler dependencies
                for func, name in component_info['int_func'].get('comp_inst_load', []):
                    instance_data_handler_list = unloaded_instance_data_handlers[name]
                    instance_data_handler_list.remove(component_class)
                    if not instance_data_handler_list:
                        del unloaded_instance_data_handlers[name]
                        for names in instance_data_handler_dependencies.values():
                            while name in names:
                                names.remove(name)

                # keep iterating while changes are happening
                keep_going = True

        if unloaded_components:
            raise ComponentLoadException('Could not resolve dependencies on {}.'.format(unloaded_components))

        # populate dependencies
        
            
            
