from hook_system.AbstractHookClient import AbstractHookClient


class VisionInfoClient(AbstractHookClient):

    def __init__(self):
        AbstractHookClient.__init__(self, "VisionInfoClient", "localhost", 55611)

    def on_debug_message(self, type, name, value):
        if "Module.Vision." in name or "Module.Ball." in name:
            self.send_message_to_service(type, name, value)

    def send_message_to_service(self, type, name, value):
        try:
            self.service_hub.send_got_message_from_robot(type, name, value)
        except:
            print "[WARNING]", str(self), "could not reach service."



