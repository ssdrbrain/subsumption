from components import *

def global_command(cmd_name, group=None):
    data = {'cmd_name': cmd_name, 'group': group}
    return function_decorator('global_command', data)

@global_component(author="Dr Brain")
@global_interface('cmdman')
@uses_global_interface('chat')
class CommandManager:
    def __init__(self):
        self.global_commands = {}
        self.global_groups = {}
    
    @component_func_data_load('global_command')
    def global_command_load(self, component, function, data):
        cmd_name = data['cmd_name']
        group = data['group'] 
        print('registered command ' + cmd_name)
        assert(cmd_name not in self.global_commands)
        self.global_commands[cmd_name] = function
        if group:
            self.global_groups.setdefault(group, []).append(cmd_name)

    @component_func_data_unload('global_command')
    def global_command_unload(self, component, function, data):
        cmd_name = data['cmd_name']
        group = data['group'] 
        print('unregistered command ' + cmd_name)
        assert(cmd_name in self.global_commands)
        del self.global_commands[cmd_name]
        if group:
            self.global_groups[group].remove(cmd_name)
    
    @interface_function()
    def do_command(self, cmd_name, params, player, target):
        if cmd_name in self.global_commands:
            self.global_commands[cmd_name](cmd_name, params, player, target)
        else:
            self.chat.send_cmd_message(player, 'no command named ' + cmd_name)
