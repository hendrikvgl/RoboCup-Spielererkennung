#-*- coding:utf-8 -*-
"""
ButtonModule
^^^^^^^^^^^^
This module reads the button input of the Darwin

History:
''''''''

* ??.??.?? Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)
"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.events import EVENT_BUTTON1_UP, EVENT_BUTTON1_DOWN
from bitbots.modules.events import EVENT_BUTTON2_UP, EVENT_BUTTON2_DOWN
from bitbots.modules.keys import DATA_KEY_IPC, DATA_KEY_BUTTON_2, DATA_KEY_BUTTON_1


class ButtonModule(AbstractModule):
    """
    A little module which reads the state of the buttons on the back of the Darwin and provides these information.

    .. hint:: The Button3 is via hardware reserved for motor reset and can therefore not be read
    """
    def __init__(self):
        self.button1 = False
        self.button2 = False

    def update(self, data):
        """
        Read status and update informations
        """
        ipc = data[DATA_KEY_IPC]
        if ipc.get_button1() and not self.button1:
            debug_m(2, "Button 1 pressed")
            data[DATA_KEY_BUTTON_1] = True
            self.button1 = True
            self.send_event(EVENT_BUTTON1_DOWN)
        else:
            data[DATA_KEY_BUTTON_1] = False
            if self.button1 and not ipc.get_button1():
                self.button1 = False
                debug_m(2, "Button 1 released")
                self.send_event(EVENT_BUTTON1_UP)
        if ipc.get_button2() and not self.button2:
            debug_m(2, "Button 2 pressed")
            data[DATA_KEY_BUTTON_2] = True
            self.button2 = True
            self.send_event(EVENT_BUTTON2_DOWN)
        else:
            data[DATA_KEY_BUTTON_2] = False
            if self.button2 and not ipc.get_button2():
                self.button2 = False
                debug_m(2, "Button 2 released")
                self.send_event(EVENT_BUTTON2_UP)


def register(ms):
        ms.add(ButtonModule, "Button",
               requires=[DATA_KEY_IPC],
               provides=[DATA_KEY_BUTTON_1,
                         DATA_KEY_BUTTON_2])
