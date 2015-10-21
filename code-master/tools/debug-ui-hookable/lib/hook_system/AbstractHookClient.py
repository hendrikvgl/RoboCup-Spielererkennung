import xmlrpclib
from hook_system.RegistryThreadClient import RegistryThreadClient


class AbstractHookClient():

    def __init__(self, name, service_ip, service_port):
        self.name = name
        self.service_ip = service_ip
        self.service_port = service_port
        self.service_hub = xmlrpclib.ServerProxy('http://%s:%i' % (service_ip, service_port),
                                                 allow_none=True, verbose=False)
        try:
            self.registry = RegistryThreadClient()
            self.registry.register(self.name, self.service_port)
        except:
            print "Client %s could not register at registry" % (name)

    def on_debug_message(self, type, name, value):
        raise NotImplementedError("Please specify what shall happen on "
                                  "Debug Message when using this HookClient")

    def __str__(self):
        return "Hook Client named %s will deliver data to %s:%i" % (self.name, self.service_ip, self.service_port)