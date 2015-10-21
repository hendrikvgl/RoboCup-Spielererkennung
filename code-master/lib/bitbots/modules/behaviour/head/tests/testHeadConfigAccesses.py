#!/usr/bin/env python
# #-*- coding:utf-8 -*-
"""
TestConfigAccesses
^^^^^^^^^^^^^^^^^^

.. moduleauthor:: Marc Bestmann <0bestman@informatik.uni-hamburg.de>

12.03.14: Created (Marc)

"""
import unittest
from bitbots.modules.behaviour.head.actions.head_to_pan_tilt import HeadToPanTilt
from bitbots.modules.behaviour.head.actions.track_object import TrackBall
from bitbots.modules.behaviour.head.decisions.continious_search import ContiniousSearch
from bitbots.modules.behaviour.head.decisions.head_duty_decider import HeadDutyDecider


class TestHeadConfigAccesses(unittest.TestCase):
    """
    This Test just initializes objects of the head modules to test the config accesses. The accesses should always be
    in the constructor, so it fails if there is a wrong value name
    """

    def test_access(self):
        self.confirm = TrackBall()
        self.head_to_pan_tilt = HeadToPanTilt((0, 0))
        self.continious_search = ContiniousSearch(0)  # todo
        self.head_duty_decider = HeadDutyDecider(0)
