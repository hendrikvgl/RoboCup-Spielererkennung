#-*- coding:utf-8 -*-
"""
Walking autoHipPitch Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Versucht den Hip Pitch anzupassen um den Roboter zu stabiliesieren, wenn er kippt.

History:
''''''''

* ??.??.??: Erstellt (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.keys import DATA_KEY_WALKING, DATA_KEY_IPC, DATA_KEY_WALKING_ACTIVE


class WalkingAutoHipPitchModule(AbstractModule):
    """
    bla TODO: besserer kommentar
    """

    def __init__(self):
        self.accel_y = 50
        #print "init bla"

    def update(self, data):
        ipc = data[DATA_KEY_IPC]
        accel = ipc.get_accel()
        self.accel_y = self.accel_y * 0.98 + accel.y * 0.02
        debug_m(4, "MitAccelY", self.accel_y)
        #print self.accel_y
        hip_pitch_change = (self.accel_y + 45) * 0.1

        if data[DATA_KEY_WALKING_ACTIVE]:
            #data["Walking.HipPitch.In"] = hip_pitch_change + data["Walking.HipPitch.Out"]
            debug_m(4, "HipPitch", data.get("Walking.HipPitch.In", -9999))


def register(ms):
    ms.add(WalkingAutoHipPitchModule, "WalkingAutoHipPitch",
           requires=[DATA_KEY_WALKING,
                     DATA_KEY_IPC,
                     DATA_KEY_WALKING_ACTIVE],
           provides=[])
