#-*- coding:utf-8 -*-
"""
For testing
"""

from bitbots.modules.abstract import AbstractModule

class DummyModule3(AbstractModule):

    def update(self, data):
        pass 


def register(ms):
    ms.add(DummyModule3, "DummyModule3",
           requires=["X"],
           provides=["Z"])
