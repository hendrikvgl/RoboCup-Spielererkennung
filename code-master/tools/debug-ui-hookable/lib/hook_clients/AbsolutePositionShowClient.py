import math
from hook_system.AbstractHookClient import AbstractHookClient
import time


class AbsolutePositionShowClient(AbstractHookClient):

    PORT = 55620

    def __init__(self):
        AbstractHookClient.__init__(self, "AbsolutePositionShowClient", "localhost", AbsolutePositionShowClient.PORT)

    def on_debug_message(self, type, name, value):
        if ".AbsolutePosition." in name:
            self.send_message_to_service(type, name, value)

    def send_message_to_service(self, type, name, value):
        try:
            self.service_hub.send_debug_message_to_hub(type, name, value)
        except:
            print "[WARNING]", str(self), "could not reach service."


if __name__ == "__main__":
    apsc = AbsolutePositionShowClient()
    c = 0
    while True:
        c += 1
        c %= 360
        a = math.pi*2* (c/360.0)
        x = int(math.sin(a) * 1000)
        y = int(math.cos(a) * 1000)
        apsc.send_message_to_service("number", "glados::Module.Bla.AbsolutePosition.x", x)
        apsc.send_message_to_service("number", "glados::Module.Bla.AbsolutePosition.y", y)
        apsc.send_message_to_service("number", "glados::Module.Bla.AbsolutePosition.o", c)
        time.sleep(0.05)