from hook_system.AbstractHookClient import AbstractHookClient


class RobotKeepAliveClient(AbstractHookClient):

    def __init__(self):
        AbstractHookClient.__init__(self, "RobotKeepAliveClient", "localhost", 55610)

    def send_message_to_service(self, robot_name):
        try:
            self.service_hub.send_got_message_from_robot(robot_name)
        except:
            print "[WARNING]", str(self), "could not reach service."

    def on_debug_message(self, type, name, value):
        robot_name = name.split("::")[0]
        self.send_message_to_service(robot_name)
