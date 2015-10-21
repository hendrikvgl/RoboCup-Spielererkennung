#-*- coding:utf-8 -*-
"""
RecalibrateBallModule
^^^^^^^^^^^^^^^^^^^^^

Notifiy the Vision to recalibrate ball


History:
''''''''

* 15.12.13: Erstellt (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)
"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_BUTTON_1, DATA_KEY_RECALIBRATE_BALL, DATA_KEY_MANUAL_PENALTY

from bitbots.util.speaker import say


class RecalibrateBallModule(AbstractModule):
    """
    Dies Klasse wartet auf button 1 und spielt dann die Animation walkready
    """

    def update(self, data):
        if data[DATA_KEY_BUTTON_1] and data.get(DATA_KEY_MANUAL_PENALTY, False):
            data[DATA_KEY_RECALIBRATE_BALL] = True
            say("Recalibrate Ball")
        else:
            data[DATA_KEY_RECALIBRATE_BALL] = False


def register(ms):
    ms.add(RecalibrateBallModule, "RecalibrateBall",
           requires=[DATA_KEY_BUTTON_1,
                     DATA_KEY_MANUAL_PENALTY],
           provides=[DATA_KEY_RECALIBRATE_BALL])
