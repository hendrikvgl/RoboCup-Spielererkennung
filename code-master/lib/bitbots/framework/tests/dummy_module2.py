#-*- coding:utf-8 -*-
"""
For testing
"""

from bitbots.modules.abstract import AbstractModule

class DummyModule2(AbstractModule):

    def update(self, data):
        pass 


def register(ms):
    ms.add(DummyModule2, "DummyModule2",
           requires=["A", "B"],
           provides=["C"])
