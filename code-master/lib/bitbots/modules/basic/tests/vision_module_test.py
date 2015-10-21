#-*- coding:utf-8 -*-
import unittest

from bitbots.modules.basic.vision.vision_module import VisionModule
from bitbots.modules.keys import DATA_KEY_GOAL_FOUND, DATA_KEY_GOAL_INFO

from bitbots.robot.pypose import PyPose
from bitbots.util.test.PyMock import PyMock

from bitbots.util import find_resource
import bitbots.util.test.testUtils as test_utils

from os import system, path


class DebugMock():
    def __init__(self):
        self.sublist = []
        self.debugMsg = []

    def sub(self, submodule):
        self.sublist.append(submodule)
        return self

    def __lshift__(self, other):
        self.debugMsg.append(other)


class TestVisionModule(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        print "#### Test VisionModule ####"


    def setUp(self):
        self.data_mock = {"Ipc": test_utils.get_init_pose(), "Debug": DebugMock()}
        # Mock the Pose
        pM = PyMock()
        pM._setSomething("HeadTilt.position", 1)
        pM._setSomething("HeadPan.position", 2)
        pM._setSomething("LAnkleRoll.position", 3)
        pM._setSomething("LAnklePitch.position", 4)
        pM._setSomething("RAnkleRoll.position", 5)
        pM._setSomething("RAnklePitch.position", 6)
        pM._setSomething("RHipPitch.position", 7)
        pM._setSomething("LHipPitch.position", 8)
        pM._setSomething("LKnee.position", 9)
        pM._setSomething("RKnee.position", 10)

        self.data_mock["Pose"] = pM

        data = {}

        tr_config = {"green_y": 55, "green_u": 30, "green_v": 15, "green_dynamic": True}

        data['ImageFormat'] = "YUYV"
        data["CameraExposureCalback"] = None
        data["CameraPose"] = PyPose()
        data["CameraResulution"] = (1280, 720)

        self.data = data

    def ignore_test_new_camera_frame_is_really_true(self):
        # Create Vision Module
        pm = VisionModule()
        pm.start(self.data)
        self.data_mock["CameraFrameVersion"] = 1
        result = pm.check_is_new_frame(self.data_mock)
        self.assertTrue(result)
        self.data_mock["CameraFrameVersion"] = 2
        result = pm.check_is_new_frame(self.data_mock)
        self.assertTrue(result)
        self.data_mock["CameraFrameVersion"] = 3
        result = pm.check_is_new_frame(self.data_mock)
        self.assertTrue(result)
        self.data_mock["CameraFrameVersion"] = 3
        result = pm.check_is_new_frame(self.data_mock)
        self.assertFalse(result)
        self.data_mock["CameraFrameVersion"] = 0
        result = pm.check_is_new_frame(self.data_mock)
        self.assertFalse(result)
        self.data_mock["CameraFrameVersion"] = 4
        result = pm.check_is_new_frame(self.data_mock)
        self.assertTrue(result)

    def ignore_test_rating_above_zero(self):
        pm = VisionModule()
        pm.start(self.data)
        self.data_mock["CameraFrameVersion"] = 1
        self.data_mock["CameraPose"] = test_utils.get_init_pose()
        ball_info = (1, (2, 3, 5))
        pm.extract_ball_infos(self.data_mock, ball_info)

        self.assertTrue(self.data_mock["BallFound"])

    def ignore_test_rating_below_zero(self):
        pm = VisionModule()
        pm.start(self.data)
        self.data_mock["CameraFrameVersion"] = 1
        self.data_mock["CameraPose"] = test_utils.get_init_pose()
        ball_info = (-1, (1, 2, 3))
        pm.extract_ball_infos(self.data_mock, ball_info)
        self.assertFalse(self.data_mock["BallFound"])

    def test_extract_goal_info(self):
        pm = VisionModule()
        pm.start(self.data)
        p = test_utils.get_init_pose()
        self.data_mock["Pose"] = p
        pm.transformer.update_pose(self.data_mock["Pose"])
        self.data_mock["CameraFrameVersion"] = 1
        goal_info = (((0,0,0),(0.0,0.0,0)), None)
        pm.extract_goal_infos(self.data_mock, goal_info)
        self.assertTrue(self.data_mock[DATA_KEY_GOAL_FOUND])
        self.assertTrue(len(self.data_mock[DATA_KEY_GOAL_INFO]) == 2)

    def test_save_color_config(self):
        pm=VisionModule()
        pm.start(self.data)

        name = "all"
        path2res = find_resource("vision-color-config/auto-color-config")

        system("rm %s/%s.png" % (path2res, name))

        pm.save_color_config(name)
        self.assertTrue(path.isfile("%s/%s.png" % (path2res, name)))


if __name__ == '__main__':
    unittest.main()
