from components import * 
from core.cmdman import global_command

@global_component(author="Dr Brain")
@uses_global_interface('chat')
class TestClass:
    @global_command("test", group="default")
    def test_command(self, cmd_name, params, player, target):
        reply = "Hello {0}!".format(player)
        self.chat.send_cmd_message(player, reply)
