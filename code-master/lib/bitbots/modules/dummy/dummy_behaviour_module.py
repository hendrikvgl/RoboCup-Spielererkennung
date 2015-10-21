#-*- coding:utf-8 -*-
"""
BehaviourModule
^^^^^^^^^^^^^^^

.. moduleauthor:: Martin Poppinga <1popping@informatik.uni-hamburg.de>

History:
* 11.12.13: Created (Martin Poppinga)

Startet das Verhalten
"""
from bitbots.modules.abstract.stack_machine_module import StackMachineModule
from bitbots.modules.behaviour.body.actions.wait import Wait
from bitbots.modules.behaviour.body.decisions.common.duty_decider import DutyDecider
from bitbots.modules.events import EVENT_GAME_STATUS_CHANGED
from bitbots.modules.events import EVENT_MANUAL_START
from bitbots.modules.keys import DATA_KEY_PENALTY, DATA_KEY_MINIMAL_BALL_TIME


class DummyBehaviourModule(StackMachineModule):

    def __init__(self):
        self.set_start_module(DutyDecider)

    def start(self, data):
        super(DummyBehaviourModule, self).start(data)
        self.register_to_event(EVENT_GAME_STATUS_CHANGED, self.change_game_status)
        self.register_to_event(EVENT_MANUAL_START, self.manual_start)

    def change_game_status(self, status):
        """reagiert auf gamestatuschanges"""
        self.connector.gamestatus_capsule().change_game_status(status)
        self.interrupt()

    def manual_start(self, status):
        """ Hält das verhalten für 20 sekunden an"""
        self.interrupt()
        self.push(Wait, 20)

def register(ms):
    ms.add(DummyBehaviourModule, "DummyBehaviourModule",
           requires=[DATA_KEY_PENALTY, DATA_KEY_MINIMAL_BALL_TIME],
           provides=["Duty"])
