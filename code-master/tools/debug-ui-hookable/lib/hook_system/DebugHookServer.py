#-*- coding:utf-8 -*-

class DebugHookServer(object):
    """
    The Main Class of the UI, which contains most functionalities
    of the UI itself, as well as some of the more basic views.
    """

    def __init__(self, server):
        print "[Setting Up Hook Server]"

        self.list_of_hooked_listeners = []

        server.add_listener(self.on_debug_message)


    def register_client(self, client):
        print "[Hook Added] ", str(client)
        self.list_of_hooked_listeners.append(client)


    def on_debug_message(self, type, name, value):
        """ Verarbeitet Debug-Nachrichten """
        for element in self.list_of_hooked_listeners:
            element.on_debug_message(type, name, value)