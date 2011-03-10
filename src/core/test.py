from components import * 
from core.cmdman import zone_command

@zone_component(author="Dr Brain")
@uses_zone_interface('chat')
class TestClass:
    @zone_command("test", group="default")
    def test_command(self, cmd_name, params, player, target):
        reply = "Hello {0}!".format(player)
        self.chat.send_cmd_message(player, reply)
