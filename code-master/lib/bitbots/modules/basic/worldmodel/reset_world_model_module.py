# coding=utf-8
"""
ResetWorldModelModule
^^^^^^^^^^^^^^^^^^^^^

Resets the believed position of the robot in the worldmodel when it gets external knowledge.

History:
''''''''

* 06.04.15: Create (Marc und Nils)
"""

from bitbots.modules.events import EVENT_GAME_STATUS_CHANGED, EVENT_NO_PENALTY
from bitbots.modules.abstract.abstract_module import AbstractModule
from bitbots.modules.keys import DATA_VALUE_STATE_READY, DATA_VALUE_STATE_INITIAL, DATA_VALUE_STATE_SET, DATA_KEY_GOAL_MODEL

class ResetWorldModelModule(AbstractModule):

    def start(self, data):

        self.register_to_event(EVENT_GAME_STATUS_CHANGED, self.game_state_change)
        self.register_to_event(EVENT_NO_PENALTY, self.set_to_own_half)
        self.worldmodule = data[DATA_KEY_GOAL_MODEL]

    def game_state_change(self, game_state):
        if game_state in [DATA_VALUE_STATE_SET, DATA_VALUE_STATE_READY, DATA_VALUE_STATE_INITIAL]:
            self.set_to_own_half(None)

    def set_to_own_half(self, event_data):
        self.worldmodule.reset_to_own()


def register(ms):
    ms.add(ResetWorldModelModule, "ResetWorldModel",
           requires=[
               DATA_KEY_GOAL_MODEL
           ],
           provides=[])
