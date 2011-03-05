from components import *

@global_component(author="Dr Brain")
@global_interface("chat")
class Chat:
    def __init__(self):
        pass

    @interface_function()
    def send_cmd_message(self, player, message):
        print("CMD MESSAGE (player={0}): {1}".format(player, message))
