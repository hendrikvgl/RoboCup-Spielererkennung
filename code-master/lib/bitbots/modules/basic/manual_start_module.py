#-*- coding:utf-8 -*-
"""
ManuelStartModule
^^^^^^^^^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* 2.414: Created (Nils Rokita)

This module let the robot wait for 20 seconds after pressing button 1.
"""


from bitbots.modules.abstract import AbstractModule
from bitbots.modules.events import EVENT_BUTTON1_DOWN, EVENT_BUTTON1_UP
from bitbots.modules.events import EVENT_MANUAL_START
from bitbots.util.speaker import say

import time

class ManuelStartModule(AbstractModule):
    def __init__(self):
        self.begin_press = 0

    def start(self, data):
        self.register_to_event(EVENT_BUTTON1_DOWN, self.down)
        self.register_to_event(EVENT_BUTTON1_UP, self.up)

    def down(self, data):
        self.begin_press = time.time()

    def up(self, down):
        if self.begin_press:
            if time.time() - self.begin_press > 2:
                say("Manual Start")
                self.send_event(EVENT_MANUAL_START)


def register(ms):
    ms.add(ManuelStartModule, "ManuelStart",
           requires=["Button1"],
           provides=[])
