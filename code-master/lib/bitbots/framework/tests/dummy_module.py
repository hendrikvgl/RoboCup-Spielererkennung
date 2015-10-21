#-*- coding:utf-8 -*-
"""
Modul um den Roboter aufstehen zu lassen


es ist nötig das animationsmodul zu laden! das passiert nicht automatisch

"""

from bitbots.modules.abstract import AbstractModule

class DummyModule(AbstractModule):
    """
    Dies Klasse wartet auf button 1 und spielt dann die Animation walkready
    """
    def update(self, data):
        pass 


def register(ms):
    ms.add(DummyModule, "DummyModule",
           requires=[],
           provides=["A", "B"])
