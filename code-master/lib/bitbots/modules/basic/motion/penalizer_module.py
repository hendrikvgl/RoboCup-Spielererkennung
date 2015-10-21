#-*- coding:utf-8 -*-
"""
PenalizerModule
^^^^^^^^^^^^^^^

This module passes the  Pnelatysatus (ManualPenalty as well as Penalty from Gamecontroller) to the motion.
Therefor it registers itself to different events.

History:
''''''''

* ??.??.?? Create (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""

from bitbots.ipc import STATE_PENALTY, STATE_CONTROLABLE
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m

from bitbots.modules.events import EVENT_PENALTY, EVENT_NO_PENALTY
from bitbots.modules.events import EVENT_MANUAL_PENALTY
from bitbots.modules.events import EVENT_NO_MANUAL_PENALTY
from bitbots.modules.events import EVENT_GLOBAL_INTERRUPT

from bitbots.modules.keys import DATA_KEY_PENALTY, DATA_KEY_MANUAL_PENALTY, DATA_KEY_IPC


class PenalizerModule(AbstractModule):
    def __init__(self):
        pass

    def start(self, data):
        self.ipc = data[DATA_KEY_IPC]
        self.data = data
        self.register_to_event(EVENT_PENALTY, self.penelize)
        self.register_to_event(EVENT_MANUAL_PENALTY, self.man_penelize)
        self.register_to_event(EVENT_NO_PENALTY, self.unpenelize)
        self.register_to_event(EVENT_NO_MANUAL_PENALTY, self.man_unpenelize)
        self.man_pen = False

    def penelize(self, event_data):
        self.ipc.set_state(STATE_PENALTY)
        debug_m(2, "Set State Penalized")
        self.send_event(EVENT_GLOBAL_INTERRUPT)

    def unpenelize(self, event_data):
        if not self.man_pen:
            # wir unpenelizen nur wenn wir nicht manuel gepenelized sind
            debug_m(2, "Unpenalize")
            self.ipc.set_state(STATE_CONTROLABLE)
            self.send_event(EVENT_GLOBAL_INTERRUPT)

    def man_penelize(self, event_data):
        self.ipc.set_state(STATE_PENALTY)
        debug_m(2, "Set State Man_Penalized")
        self.send_event(EVENT_GLOBAL_INTERRUPT)
        self.man_pen = True

    def man_unpenelize(self, event_data):
        debug_m(2, "Man_Unpenalize")
        self.ipc.set_state(STATE_CONTROLABLE)
        self.send_event(EVENT_GLOBAL_INTERRUPT)
        self.man_pen = False



def register(ms):
    ms.add(PenalizerModule, "Penalizer",
           requires=[DATA_KEY_IPC,
                     DATA_KEY_PENALTY,
                     DATA_KEY_MANUAL_PENALTY],
           provides=[])
