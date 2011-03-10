from components import *

def zone_command(cmd_name, group=None):
    data = {'cmd_name': cmd_name, 'group': group}
    return function_decorator('zone_command', data)

def arena_command(cmd_name, group=None):
    data = {'cmd_name': cmd_name, 'group': group}
    return function_decorator('arena_command', data)

@zone_component(author="Dr Brain")
@reg_interface('cmdman')
@uses_interface('chat')
class CommandManager:
    def __init__(self):
        self.zone_commands = {}
        self.zone_groups = {}
        self.arena_commands = {}
        self.arena_groups = {}
    
    @component_func_data_load('zone_command')
    def zone_command_load(self, component, function, data):
        cmd_name = data['cmd_name']
        group = data['group'] 
        print('registered command ' + cmd_name)
        assert(cmd_name not in self.zone_commands)
        self.zone_commands[cmd_name] = function
        if group:
            self.zone_groups.setdefault(group, []).append(cmd_name)

    @component_func_data_unload('zone_command')
    def zone_command_unload(self, component, function, data):
        cmd_name = data['cmd_name']
        group = data['group'] 
        print('unregistered command ' + cmd_name)
        assert(cmd_name in self.zone_commands)
        del self.zone_commands[cmd_name]
        if group:
            self.zone_groups[group].remove(cmd_name)
    
    @interface_function()
    def do_command(self, cmd_name, params, player, target):
        if cmd_name in self.zone_commands:
            self.zone_commands[cmd_name](cmd_name, params, player, target)
        else:
            self.chat.send_cmd_message(player, 'no command named ' + cmd_name)
