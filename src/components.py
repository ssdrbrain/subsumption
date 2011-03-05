
def _get_function_info(func):
    """Creates a function's function_info, or returns it if it exists.""" 
    try:
        function_info = func.function_info
    except AttributeError:
        function_info = {'int_func': {}, 'ext_func': {}}
        func.function_info = function_info
    return function_info

def _get_component_info(cls):
    """Creates a components's component_info, or returns it if it exists."""
    try:
        component_info = cls.component_info
    except AttributeError:
        component_info = {'int_comp': {}, 'ext_comp': {},
                          'int_func': {}, 'ext_func': {}}
        cls.component_info = component_info
    return component_info

def _component_decorator(author, type):
    """This does the heavy lifting of component creation. It's called by the 
    various decorators that create components (e.g. global_component)."""
    def decorator(cls):
        component_info = _get_component_info(cls)
        component_info[type] = True
        if author:
            component_info['author'] = author

        # make sure functions haven't been handled already
        if not component_info['int_func'] and not component_info['ext_func']:
            # copy the all the function_info into component_info
            for func in cls.__dict__.values():
                try:
                    function_info = func.function_info
                    for name, data in function_info['int_func'].items():
                        component_info['int_func'].setdefault(name, []).append((func, data))
                    for name, data in function_info['ext_func'].items():
                        component_info['ext_func'].setdefault(name, []).append((func, data))
                except AttributeError:
                    pass
        return cls
    return decorator

def global_component(author=None):
    """Decorator for creating a component for loading at the global level."""
    return _component_decorator(author, 'global')

def _general_function_decorator(section, name, data, chain_data=False):
    """Decorator for adding to function_info[section][name]."""
    assert(type(name).__name__ == 'str')
    def decorator(func):
        function_info = _get_function_info(func)
        if chain_data:
            function_info[section].setdefault(name, []).append(data)
        else:
            assert(name not in function_info[section])
            function_info[section][name] = data
        return func
    return decorator

def function_decorator(name, data, chain_data=False):
    """Decorator for adding data to a function for consumption by a 
    component_func_data_load function."""
    return _general_function_decorator('ext_func', name, data, chain_data)

def _general_component_decorator(section, name, data, chain_data=False):
    """Decorator for adding to component_info[section][name]."""
    assert(type(name).__name__ == 'str')
    def decorator(cls):
        component_info = _get_component_info(cls)
        if chain_data:
            component_info[section].setdefault(name, []).append(data)
        else:
            assert(name not in component_info[section])
            component_info[section][name] = data
        return cls
    return decorator

def component_decorator(name, data, chain_data=False):
    """Decorator for adding data to a component for consumption by a
    component_instance_data_load function."""
    return _general_component_decorator('ext_comp', name, data, chain_data)

def global_interface(name):
    """Decorator for registering a global interface."""
    return _general_component_decorator('int_comp', 'global_interface', name, chain_data=True)

def interface_function(interface=None):
    """Decorator for adding a function to a registered interface."""
    return _general_function_decorator('int_func', 'interface_function', interface, chain_data=True)

def uses_global_interface(name, int_func_name=None):
    """Decorator for using a global interface."""
    if not int_func_name:
        int_func_name = name
    def decorator(cls):
        _general_component_decorator('int_comp', 'uses_global_interface', name, chain_data=True)(cls)
        try:
            old_init = cls.__init__
        except AttributeError:
            old_init = None
        def new_init(self, *args, **interfaces):
            assert(name in interfaces)
            assert(int_func_name not in cls.__dict__)
            self.__dict__[int_func_name] = interfaces[name]
            del interfaces[name]
            if old_init:
                old_init.__get__(self)(*args, **interfaces)
        cls.__init__ = new_init
        return cls
    return decorator

def component_func_data_load(name):
    return _general_function_decorator('int_func', 'comp_func_load', name)

def component_func_data_unload(name):
    return _general_function_decorator('int_func', 'comp_func_unload', name)

def component_instance_data_load(name):
    return _general_function_decorator('int_func', 'comp_inst_load', name)

def component_instance_data_unload(name):
    return _general_function_decorator('int_func', 'comp_inst_unload', name)

