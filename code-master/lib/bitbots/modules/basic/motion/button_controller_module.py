#-*- coding:utf-8 -*-
"""
BottonControllerModule
^^^^^^^^^^^^^^^^^^^^^^

This module provides a simple controll for the robot via the buttons on the back of the robot.

History:
''''''''

* ??.??.?? Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_CONFIG, DATA_KEY_BUTTON_1, DATA_KEY_BUTTON_2, DATA_KEY_WALKING, \
    DATA_KEY_WALKING_ACTIVE, DATA_KEY_WALKING_FORWARD, DATA_KEY_ANIMATION
from bitbots.util.speaker import say


class ButtonControllerModule(AbstractModule):
    """
    The Buttonmodule defines currently 2 modes. One can switch between them.

    By pressing Button1 the mode is switched. By pressing Button2 the coresponding action is started,

     Available modes:

    * Init: Initialstate, does nothing

    * Walking: Run straight forward (Button1 = start/stop)

    * Anim: Plays animation (Handstand)
    """
    def __init__(self):
        self.actual_state = "init"

    def start(self, data):
        config = data[DATA_KEY_CONFIG]
        self.conf_hands = config["hands"]

    def update(self, data):
        """
        Checks buttons and changes state corespondingly
        """
        if data[DATA_KEY_BUTTON_1]:
            if self.actual_state == 'walking':
                self.actual_state = 'anim'
                say("Play Anim Mode")
            elif self.actual_state == 'init' or \
                    self.actual_state == 'anim':
                self.actual_state = 'walking'
                say("Walking Mode")

        if data[DATA_KEY_BUTTON_2]:
            if self.actual_state == 'walking':
                # if nothing was setted, return false
                if data.get(DATA_KEY_WALKING_ACTIVE, False):
                    say("stop")
                    data[DATA_KEY_WALKING_ACTIVE] = False
                    data[DATA_KEY_WALKING_FORWARD] = 0
                else:
                    say("walk")
                    data[DATA_KEY_WALKING_ACTIVE] = True
                    data[DATA_KEY_WALKING_FORWARD] = 3
            if self.actual_state == 'anim':
                if self.conf_hands:
                    data[DATA_KEY_ANIMATION] = "test_arm"

                else:
                    data[DATA_KEY_ANIMATION] = "headstand_new_head"


def register(ms):
    ms.add(ButtonControllerModule, "ButtonController",
           requires=[DATA_KEY_BUTTON_1,
                     DATA_KEY_BUTTON_2,
                     DATA_KEY_WALKING,
                     DATA_KEY_WALKING_ACTIVE,
                     DATA_KEY_WALKING_FORWARD,
                     DATA_KEY_CONFIG],
           provides=[])
