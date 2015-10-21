#-*- coding:utf-8 -*-
"""
TestLocalWorldModelModule
^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 5/4/14: Created (sheepy)

"""
import unittest
import mock

from bitbots.modules.basic.worldmodel.local_goal_model_module import LocalGoalModelModule
from bitbots.modules.keys import DATA_KEY_IS_NEW_FRAME


class TestLocalWorldModelModule(unittest.TestCase):

    def test_sends_debug_only_on_new_frame(self):
        lwmm = LocalGoalModelModule()

        return_value = lwmm.update({
            DATA_KEY_IS_NEW_FRAME: False
        })

        self.assertEquals(-1, return_value)

    def test_on_new_frame_publish_methods_are_called(self):
        lwmm = LocalGoalModelModule()

        publish_ball_info_mock = mock.MagicMock()
        lwmm.publish_ball_info = publish_ball_info_mock

        publish_goal_info_mock = mock.MagicMock()
        lwmm.publish_goal_info = publish_goal_info_mock

        publish_ball_info_prediction_mock = mock.MagicMock()
        lwmm.publish_ball_info_prediction = publish_ball_info_prediction_mock

        publish_obstacle_info_mock = mock.MagicMock()
        lwmm.publish_obstacle_info = publish_obstacle_info_mock

        data = {
            DATA_KEY_IS_NEW_FRAME: True
        }

        lwmm.start(data)
        return_value = None
        for i in range(41):
            return_value = lwmm.update(data)

        publish_ball_info_mock.assert_called_once_with(data)
        publish_goal_info_mock.assert_called_once_with(data)
        publish_obstacle_info_mock.assert_called_once_with(data)
        publish_ball_info_prediction_mock.assert_called_once_with(data)
        self.assertEquals(None, return_value)
