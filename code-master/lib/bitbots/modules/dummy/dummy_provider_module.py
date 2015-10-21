#-*- coding:utf-8 -*-
"""

^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 5/5/14: Created (sheepy)

"""
import os
import time

from bitbots.modules.abstract.abstract_module import AbstractModule
from bitbots.modules.basic.vision.vision_objects import BallInfo
from bitbots.modules.basic.worldmodel.local_goal_model_module import LocalGoalModel
from bitbots.modules.keys import DATA_KEY_IS_NEW_FRAME, DATA_KEY_GOAL_FOUND, DATA_KEY_GOAL_INFO, DATA_KEY_GAME_STATUS, \
    DATA_VALUE_STATE_PLAYING, DATA_KEY_BALL_FOUND, DATA_KEY_OBSTACLE_FOUND, DATA_KEY_OBSTACLE_INFO, DATA_KEY_BALL_INFO, DATA_KEY_GOAL_MODEL, DATA_KEY_CAMERA_CAPTURE_TIMESTAMP, DATA_KEY_POSITION
from bitbots.modules.dummy.world_service_client import WorldServiceClient
from bitbots.util.speaker import say
from bitbots.util.test import testUtils


class DummyProviderModule(AbstractModule):
    def __init__(self):
        self.index = 9999999

        self.num_times = 0

        self.next = None

        # Initialize the Client with its parameters
        host = os.environ["DP_HOST"]
        port = int(os.environ["DP_PORT"])
        self.player = os.environ["PLAYER"]

        self.worldServiceClient = WorldServiceClient(host, port)

        self.last_f = 0
        self.last_s = 0
        self.last_a = 0
        self.lastactive = False


    def start(self, data):
        data["Pose"] = testUtils.get_init_pose()
        data["Ipc"] = testUtils.get_Ipc()
        data[DATA_KEY_GOAL_MODEL] = LocalGoalModel()
        self.worldServiceClient.register_robot(self.player)

    def update_walking(self, data):
        """ This method updates the Walking Parameters from the data dictionary to the world service """

        f = data.get("Walking.Forward", 0)
        s = data.get("Walking.Sideward", 0)
        a = data.get("Walking.Angular", 0)
        active = data.get("Walking.Active", False)

        if self.last_f != f or self.last_s != s or self.last_a != a or self.lastactive != active:
            self.last_f = f
            self.last_s = s
            self.last_a = a
            self.lastactive = active
            self.worldServiceClient.update_walking_for(self.player, f, s, a, active)

    def update_game_status(self, data):
        gamestate = data.get(DATA_KEY_GAME_STATUS, DATA_VALUE_STATE_PLAYING)


    def update(self, data):
        # First of all update all teh walking parameters
        self.update_walking(data)

        current_data = self.worldServiceClient.get_update_info(self.player)

        data[DATA_KEY_IS_NEW_FRAME] = True
        data[DATA_KEY_BALL_FOUND] = True
        data[DATA_KEY_GOAL_FOUND] = False
        data[DATA_KEY_OBSTACLE_FOUND] = False
        data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP] = time.time()

        u, v, distance = current_data

        data[DATA_KEY_BALL_INFO] = BallInfo(*[u, v, 0, 0, 10, 1, distance])


    def post(self, data):
        """
        Dieses Modul tut seine Arbeit in :func:`post` damit von Modulen
        eingereichte Animationen direkt gespielt werden können auch
        wenn diese Animation requiren und das Modul sonst zuerst
        ausgeführt wird
        """
        if data.get("Animation", None) is not None:

            if data["Animation"][0] in ["rk_go14", "lk_io14"]:
                self.worldServiceClient.kick_ball(self.player)
            if data["Animation"][0] in ["r-pass"]:
                say("Kick Right Side")
                self.worldServiceClient.kick_ball_side(self.player, "right")
            if data["Animation"][0] in ["l-pass"]:
                say("Kick Left Side")
                self.worldServiceClient.kick_ball_side(self.player, "left")
            print data["Animation"]
            data["Animation"][1](False)
            data["Animation"] = None


def register(ms):
    ms.add(DummyProviderModule, "DummyProvider",
           requires=[DATA_KEY_POSITION],
           provides=[DATA_KEY_IS_NEW_FRAME,
                     DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO,
                     DATA_KEY_GOAL_FOUND, DATA_KEY_GOAL_INFO,
                     DATA_KEY_OBSTACLE_FOUND, DATA_KEY_OBSTACLE_INFO,
                     DATA_KEY_GOAL_MODEL, DATA_KEY_CAMERA_CAPTURE_TIMESTAMP,
                     "Ipc", "Pose"])
