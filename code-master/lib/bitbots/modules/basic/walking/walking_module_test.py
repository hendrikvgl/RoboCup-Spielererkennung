#-*- coding:utf-8 -*-
"""
Ein kleines Testmodul welches den Roboter etwas laufen lässt

"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m

from bitbots.modules.keys import DATA_KEY_IPC, DATA_KEY_WALKING


class WalkingTestModule(AbstractModule):
    """
    Loslaufen und wieder anhalten, und dann nochmal...
    """

    def __init__(self):
        self.i = 0

    def update(self, data):
        ipc = data[DATA_KEY_IPC]
        gyro = ipc.get_gyro()
        debug_m(4, "gyro.x", gyro.x)
        debug_m(4, "gyro.y", gyro.y)
        debug_m(4, "gyro.z", gyro.z)
        accel = ipc.get_accel()
        debug_m(4, "accel.x", accel.x)
        debug_m(4, "accel.y", accel.y)
        debug_m(4, "accel.z", accel.z)


def register(ms):
    ms.add(WalkingTestModule, "WalkingTest",
           requires=[DATA_KEY_WALKING, DATA_KEY_IPC],
           provides=[])
