#-*- coding:utf-8 -*-
"""
BallTimeModule
^^^^^^^^^^^^^^

This module tries to compute how long we need to reach the ball.

History:
''''''''

* 08.03.14: Erstellt (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_BALL_TIME, DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO


class BallTimeModule(AbstractModule):

    def update(self, data):
        if data[DATA_KEY_BALL_FOUND]:
            data[DATA_KEY_BALL_TIME] = (data[DATA_KEY_BALL_INFO].distance / 1000.0) * 150 + 15
            # TODO das ist nicht gut so
        else:
            data[DATA_KEY_BALL_TIME] = 99999999



def register(ms):

    ms.add(BallTimeModule, "BallTime",
           requires=[DATA_KEY_BALL_FOUND,
                     DATA_KEY_BALL_INFO],
           provides=[DATA_KEY_BALL_TIME])
