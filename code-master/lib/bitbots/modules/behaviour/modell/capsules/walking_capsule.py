# -*- coding:utf-8 -*-
"""
WalkingCapsule
^^^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 4/16/14: Created (sheepy)

"""

from bitbots.debug import Scope
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.util import get_config


class WalkingCapsule(object):
    # Nothing (Represents a 0)
    ZERO = "ZERO"

    # Forward-Backward
    SLOW_BACKWARD = "SLOW_BACKWARD"
    MEDIUM_BACKWARD = "MEDIUM_BACKWARD"
    FAST_BACKWARD = "FAST_BACKWARD"

    SLOW_FORWARD = "SLOW_FORWARD"
    MEDIUM_FORWARD = "MEDIUM_FORWARD"
    FAST_FORWARD = "FAST_FORWARD"

    # Left-Right
    SLOW_SIDEWARDS_LEFT = "SLOW_SIDEWARDS_LEFT"
    MEDIUM_SIDEWARDS_LEFT = "MEDIUM_SIDEWARDS_LEFT"
    FAST_SIDEWARDS_LEFT = "FAST_SIDEWARDS_LEFT"

    SLOW_SIDEWARDS_RIGHT = "SLOW_SIDEWARDS_RIGHT"
    MEDIUM_SIDEWARDS_RIGHT = "MEDIUM_SIDEWARDS_RIGHT"
    FAST_SIDEWARDS_RIGHT = "FAST_SIDEWARDS_RIGHT"

    # Angular Turn Left, Right
    SLOW_ANGULAR_LEFT = "SLOW_ANGULAR_LEFT"
    MEDIUM_ANGULAR_LEFT = "MEDIUM_ANGULAR_LEFT"
    FAST_ANGULAR_LEFT = "FAST_ANGULAR_LEFT"

    SLOW_ANGULAR_RIGHT = "SLOW_ANGULAR_RIGHT"
    MEDIUM_ANGULAR_RIGHT = "MEDIUM_ANGULAR_RIGHT"
    FAST_ANGULAR_RIGHT = "FAST_ANGULAR_RIGHT"

    def __init__(self, data):
        self.debug = Scope("Connector.Capsule.WalkingCapsule")
        self.data = data

        config = get_config()["Behaviour"]["Common"]["Walking"]

        self.forward_dict = {
            element: config[element] for element in [
                WalkingCapsule.SLOW_BACKWARD, WalkingCapsule.MEDIUM_BACKWARD, WalkingCapsule.FAST_BACKWARD,
                WalkingCapsule.SLOW_FORWARD, WalkingCapsule.MEDIUM_FORWARD, WalkingCapsule.FAST_FORWARD
            ]
        }
        self.forward_dict[WalkingCapsule.ZERO] = 0

        self.sidewards_dict = {
            element: config[element] for element in [
                WalkingCapsule.SLOW_SIDEWARDS_LEFT, WalkingCapsule.MEDIUM_SIDEWARDS_LEFT,
                WalkingCapsule.FAST_SIDEWARDS_LEFT,
                WalkingCapsule.SLOW_SIDEWARDS_RIGHT, WalkingCapsule.MEDIUM_SIDEWARDS_RIGHT,
                WalkingCapsule.FAST_SIDEWARDS_RIGHT
            ]
        }
        self.sidewards_dict[WalkingCapsule.ZERO] = 0

        self.angular_dict = {
            element: config[element] for element in [
                WalkingCapsule.SLOW_ANGULAR_LEFT, WalkingCapsule.MEDIUM_ANGULAR_LEFT,
                WalkingCapsule.FAST_ANGULAR_LEFT,
                WalkingCapsule.SLOW_ANGULAR_RIGHT, WalkingCapsule.MEDIUM_ANGULAR_RIGHT,
                WalkingCapsule.FAST_ANGULAR_RIGHT
            ]
        }
        self.angular_dict[WalkingCapsule.ZERO] = 0

        self.forward_correction_offset = 0
        self.angular_correction_offset = 0
        self.sidewards_correction_offset = 0

    def start_walking_plain(self, forward, angular, sideward=0):
        """ This Method allows numeric values """
        self.data["Walking.Sideward"] = sideward
        self.data["Walking.Forward"] = forward
        self.data["Walking.Angular"] = angular
        self.data["Walking.Active"] = True

    def start_walking(self, forward_key=ZERO, angular_key=ZERO, sidewards_key=ZERO):
        # Assert that the key is valid

        assert forward_key in self.forward_dict.keys()
        assert angular_key in self.angular_dict.keys()
        assert sidewards_key in self.sidewards_dict.keys()

        f, a, s = self.get_walking_correction_values()

        self.data["Walking.Forward"] = self.forward_dict[forward_key] + f
        self.data["Walking.Angular"] = self.angular_dict[angular_key] + a
        self.data["Walking.Sideward"] = self.sidewards_dict[sidewards_key] + s

        # Make sure walking only starts with at least one key unequal to zero
        if len([e for e in [forward_key, angular_key, sidewards_key] if e != WalkingCapsule.ZERO]) > 0:
            self.data["Walking.Active"] = True
            debug_m(3, "WalkingActive", True)

    def set_angular_direct(self, value):
        self.data["Walking.Angular"] = value

    def get_walking_correction_values(self):
        """This method is delivers three values that are applied additionally
            to every call to the walking engine - that can be used for correction of single robots """
        return self.forward_correction_offset, self.angular_correction_offset, self.sidewards_correction_offset

    def stop_walking(self):
        """ This method stops the walking - note that it could take some time until the robot is standing """
        self.data["Walking.Sideward"] = 0
        self.data["Walking.Forward"] = 0
        self.data["Walking.Angular"] = 0
        self.data["Walking.Active"] = False

    def is_walking(self):
        """ This method returns True if the walking is actually not running """
        return not self.data["Walking.Running"]
