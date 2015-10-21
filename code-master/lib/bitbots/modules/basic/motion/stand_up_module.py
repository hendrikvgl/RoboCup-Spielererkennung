#-*- coding:utf-8 -*-
"""
StandUpModule
^^^^^^^^^^^^^

Makes the robot stand up

.. Warning::
    It is necessary to load :mod:`bitbots.modules.basic.motion.AnimationModule`. This doesnt happen automaticly!

History:
''''''''

* ??.??.?? Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_CONFIG, DATA_KEY_ANIMATION, DATA_KEY_MANUAL_PENALTY
from bitbots.modules.keys import DATA_KEY_BUTTON_1
from bitbots.util.speaker import say


class StandUpModule(AbstractModule):
    """
    This class waits for Button1 and plays then the animation walkready
    """

    def update(self, data):
        if data[DATA_KEY_BUTTON_1] and not data.get(DATA_KEY_MANUAL_PENALTY, False):
            data[DATA_KEY_ANIMATION] = str(data[DATA_KEY_CONFIG]["animations"]["motion"]["walkready"])
            say("Stand up")


def register(ms):
    ms.add(StandUpModule, "StandUp",
           requires=[DATA_KEY_BUTTON_1,
                     DATA_KEY_CONFIG,
                     DATA_KEY_MANUAL_PENALTY],
           provides=[])
