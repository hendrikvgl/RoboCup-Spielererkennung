# -*- coding:utf-8 -*-
"""
Connector
^^^^^^^^^

.. moduleauthor:: Martin Poppinga <1popping@informatik.uni-hamburg.de>

History:
* 14.12.13: Created (Martin Poppinga)

* 18.08.2014 Capseln gerefactored

Kapselt das das Data-Array für das Verhalten
"""
from bitbots.debug import Scope

from bitbots.modules.behaviour.modell.capsules.animation_capsule import AnimationCapsule
from bitbots.modules.behaviour.modell.capsules.blackboard_capsule import BlackboardCapsule
from bitbots.modules.behaviour.modell.capsules.filtered_vision_capsule import FilteredVisionCapsule
from bitbots.modules.behaviour.modell.capsules.game_status_capsule import GameStatusCapsule
from bitbots.modules.behaviour.modell.capsules.world_model_capsule import WorldModelCapsule
from bitbots.modules.behaviour.modell.capsules.raw_vision_capsule import RawVisionCapsule
from bitbots.modules.behaviour.modell.capsules.team_data_capsule import TeamDataCapsule
from bitbots.modules.behaviour.modell.capsules.walking_capsule import WalkingCapsule
from bitbots.modules.keys import DATA_KEY_ROLE
from mitecom.mitecom import ROLE_SUPPORTER, ROLE_GOALIE, ROLE_OTHER
from bitbots.robot.kinematics import *

config = get_config()


class Connector:
    """
    Schnittstelle zum Weltmodell.
    Aus dem Verhalten soll hierdrauf zugegriffen werden anstatt auf das data-Array direkt
    """

    def __init__(self, data):
        self.debug = Scope("Behaviour.Connector")
        self.data = data

        # This is the Gateway to the WalkingCapsule which handles all walking related stuff
        self._gamestate = GameStatusCapsule(data)
        self._walking = WalkingCapsule(data)
        self._blackboard = BlackboardCapsule(data)
        self._team_data = TeamDataCapsule(data)
        self._animation = AnimationCapsule(data)
        self._raw_vision = RawVisionCapsule(data)
        self._filtered_vision = FilteredVisionCapsule(data)
        self._world_model = WorldModelCapsule(data)

        self._robot = Robot()
        self._kinematic_task = KinematicTask(self._robot)

    def __getitem__(self, item):
        """
        Fallbacklösung, falls noch versucht wird auf das dataarray zuzugreifen
        """
        assert item in self.data
        return self.data[item]

    def is_key_in_data(self, key):
        return key in self.data

    def get_pose(self):
        return self.data["Pose"]

    def set_pose(self, pose):
        self.data["Ipc"].update(pose)

    def get_ipc(self):
        return self.data["Ipc"]

    def set_duty(self, duty):
        self.data["Duty"] = duty
        role = ROLE_OTHER
        if duty == "Goalie":
            role = ROLE_GOALIE
        if duty in ("Fieldie", "TeamPlayer"):
            role = ROLE_SUPPORTER
        self.data[DATA_KEY_ROLE] = role

    def get_duty(self):
        return self.data.get("Duty", False)

    def get_robot(self):
        return self._robot

    def get_kinematic_task(self):
        return self._kinematic_task

    ################
    # ## Capsules ##
    ################

    def walking_capsule(self):
        """ This is the Gateway to the WalkingCapsule which handles all walking related stuff """
        return self._walking

    def blackboard_capsule(self):
        """ This is the Gateway to the BehaviourBlackboardCapsule which includes
            data to be memorized by the behaviour """
        return self._blackboard

    def gamestatus_capsule(self):
        """ This is the Gateway to the GameStatusCapsule which includes
            data like gamestate and other things coming from GC """
        return self._gamestate

    def team_data_capsule(self):
        """ This is the Gateway to the TeamDataCapsule which provides information about TeamMates and allows
            writing info to them (later) """
        return self._team_data

    def animation_capsule(self):
        """ This is the Gateway to the AnimationCapsule which provides information about the Animations
            and can be used to schedule animations """
        return self._animation

    def raw_vision_capsule(self):
        """ This is the gateway to the raw data provided by the vision """
        return self._raw_vision

    def filtered_vision_capsule(self):
        """ This is the gateway to the Filtered VisionInfo Capsule which gives information about,
            filtered data, overtime data and estimations - basically data further processed that came
            from the vision """
        return self._filtered_vision

    def world_model_capsule(self):
        return self._world_model
