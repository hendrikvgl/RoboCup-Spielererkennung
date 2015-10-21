#-*- coding:utf-8 -*-
"""
Torjubel
^^^^^^^^

Does goal jubilation

History:
''''''''

* 7.4.14: Created (Nils Rokita)

"""

from bitbots.modules.abstract.abstract_module import AbstractModule
from bitbots.modules.events import EVENT_GOAL
from bitbots.util import get_config
from bitbots.util.speaker import say


class Torjubel(AbstractModule):

    def __init__(self):
        config = get_config()
        self.anim = config["animations"]["motion"]["torjubel"]

    def start(self, data):
        self.register_to_event(
            EVENT_GOAL,
            lambda arg: self.torjubel(data, arg))

    def torjubel(self, data, tore):
        say("Huchee!")
        data["Animation"] = self.anim


def register(ms):
    ms.add(Torjubel, "Torjubel",
           requires=[EVENT_GOAL],
           provides=[])
