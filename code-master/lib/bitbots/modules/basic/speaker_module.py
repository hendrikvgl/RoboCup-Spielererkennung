#-*- coding:utf-8 -*-
"""
SpeakerModule
^^^^^^^^^^^^^

Does accoustic output of game status and penalty

Configvalue: SPEAK (true/false) if there should be output

History:
''''''''

* 1.4.12: Created (Nils Rokita)

* 9.1.14: Changed to normal moduel without threadiong, because not necessary

* 06.08.14 Refactor (Marc Bestmann)

"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.events import EVENT_PENALTY, EVENT_NO_PENALTY
from bitbots.modules.events import EVENT_GAME_STATUS_CHANGED

from bitbots.modules.keys import DATA_KEY_CONFIG, DATA_KEY_PENALTY, DATA_KEY_GAME_STATUS
from bitbots.util.speaker import say


class SpeakerModule(AbstractModule):

    def start(self, data):
        self.SPEAK = data[DATA_KEY_CONFIG]["SPEAK"]
        self.oldgamestate = None
        if self.SPEAK:
            self.register_to_event(EVENT_PENALTY,
                lambda data: say("Nooo. I am Penalized"))
            self.register_to_event(EVENT_NO_PENALTY,
                lambda data: say("Jeah! I can play again"))
            self.register_to_event(EVENT_GAME_STATUS_CHANGED,
                lambda data: say(data))


def register(ms):

    ms.add(SpeakerModule, "Speaker",
           requires=[DATA_KEY_CONFIG,
                     DATA_KEY_GAME_STATUS,
                     DATA_KEY_PENALTY],
           provides=[])
