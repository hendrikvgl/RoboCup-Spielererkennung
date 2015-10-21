# -*- coding:utf-8 -*-
import xmlrpclib


class RegistryThreadClient():

    def __init__(self):
        self.service = xmlrpclib.ServerProxy('http://localhost:55600', allow_none=True, verbose=False)

    def register(self, name, port):
        return self.service.register(name, port)

    def has_registered(self, name):
        return self.service.has_registered(name)

    def get_port_by_name(self, name):
        return self.service.get_port_by_name(name)