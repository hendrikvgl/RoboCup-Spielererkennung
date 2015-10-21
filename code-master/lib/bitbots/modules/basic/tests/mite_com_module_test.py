#-*- coding:utf-8 -*-
"""
MiteComTestModule
^^^^^^^^^^^^^^^^^

Ein test für mitecom

**Requires**:

**Provides**:

"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m

from bitbots.modules.keys import DATA_KEY_MINIMAL_BALL_TIME, DATA_KEY_BALL_TIME, DATA_KEY_ROLE
from mitecom.mitecom import ROLE_SUPPORTER, ROLE_STRIKER

class MiteComTestModule(AbstractModule):
    """

    """

    def update(self, data):
        #print data[DATA_KEY_MINIMAL_BALL_TIME] , data[DATA_KEY_BALL_TIME]
        if data[DATA_KEY_MINIMAL_BALL_TIME] < data[DATA_KEY_BALL_TIME]:
            debug_m(2, "Other is nearer")
            data['Animation'] = "goalie_mitte2"
            data[DATA_KEY_ROLE] = ROLE_SUPPORTER
        else:
            debug_m(2, "Striker")
            data['Animation'] = "goalie_left_shoulder"
            data[DATA_KEY_ROLE] = ROLE_STRIKER


def register(ms):

    ms.add(MiteComTestModule, "MiteComTest",
           requires=[DATA_KEY_MINIMAL_BALL_TIME,
                    DATA_KEY_BALL_TIME],
           provides=[])
