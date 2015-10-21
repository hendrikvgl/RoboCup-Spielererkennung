#-*- coding:utf-8 -*-
"""
ManualPenalizerModule
^^^^^^^^^^^^^^^^^^^^^

Module for penalyzing the robot manually by pressing a button

History:
''''''''

* ??.??.?? Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.events import EVENT_BUTTON2_DOWN
from bitbots.modules.events import EVENT_MANUAL_PENALTY
from bitbots.modules.events import EVENT_NO_MANUAL_PENALTY
from bitbots.util.speaker import say

from bitbots.modules.keys import DATA_KEY_MANUAL_PENALTY, DATA_KEY_BUTTON_2


class ManualPenalizerModule(AbstractModule):
    """
    This class waits for button2 and changes the ManualPenalty state.
    ManulaPenalty is equal to penalty
    """

    def start(self, data):
        self.register_to_event(EVENT_BUTTON2_DOWN, self.switch_manual_penalty)
        self.penalty = False

    def switch_manual_penalty(self, data):
        if not self.penalty:
            self.send_event(EVENT_MANUAL_PENALTY)
            say("Set Manual Penalty")
            self.penalty = True
        else:
            self.send_event(EVENT_NO_MANUAL_PENALTY)
            say("Revoke Manual Penalty")
            self.penalty = False


def register(ms):
    ms.add(ManualPenalizerModule, "ManualPenalizer",
           requires=[DATA_KEY_BUTTON_2],
           provides=[DATA_KEY_MANUAL_PENALTY])
