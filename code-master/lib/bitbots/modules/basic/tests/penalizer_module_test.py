#-*- coding:utf-8 -*-
import unittest

from bitbots.ipc import STATE_PENALTY, STATE_CONTROLABLE
from bitbots.modules.keys import DATA_KEY_PENALTY
from bitbots.modules.basic.motion.penalizer_module import PenalizerModule


class IPCMock():
    def __init__(self):
        self.state = STATE_CONTROLABLE

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state


class DebugMock():
    def __init__(self):
        self.sublist = []
        self.debugMsg = []

    def sub(self, submodule):
        self.sublist.append(submodule)
        return self

    def __lshift__(self, other):
        self.debugMsg.append(other)


class TestPenalizerModule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):   
        print "#### Test PenalizerModule ####"

    def setUp(self):
        self.data_mock = {"Ipc": IPCMock(), "Debug": DebugMock()}

    def ignore_test_isPenalizedOnPenalty_is_false(self):
        # Create Penalizer Module
        pm = PenalizerModule()
        # Add Relevant Mock Data to Dictionary
        self.data_mock[DATA_KEY_PENALTY] = False
        # Call the Penalty Module
        pm.update(self.data_mock)
        self.assertEquals(STATE_CONTROLABLE, self.data_mock["Ipc"].get_state())

    def ignore_test_isPenalizedOnPenalty_is_true(self):
        # Create Penalizer Module
        pm = PenalizerModule()
        # Add Relevant Mock Data to Dictionary
        self.data_mock[DATA_KEY_PENALTY] = True
        # Call the Penalty Module
        pm.update(self.data_mock)
        self.assertEquals(STATE_PENALTY, self.data_mock["Ipc"].get_state())

if __name__ == '__main__':
    unittest.main()
