#-*- coding:utf-8 -*-

"""
BallSpeedModule
^^^^^^^^^^^^^^^
This module tries to compute the velocity and current moving direction in relation to ourself.

measured in mm/s

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:
''''''''

* 06.03.13: Created (Sheepy Keßler)

* 14.3.14: complete Refactor and fixing (Nils Rokita & Marc Bestmann)

* 06.08.14 Refactor (Marc Bestmann)


"""
import math

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.keys import DATA_KEY_BALL_SPEED, DATA_KEY_BALL_VECTOR, DATA_KEY_CAMERA_CAPTURE_TIMESTAMP, \
    DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO, DATA_KEY_IPC, DATA_KEY_POSE, DATA_KEY_WALKING, DATA_KEY_IS_NEW_FRAME


class BallSpeedModule(AbstractModule):
    """ Very simple implementation, to determine how fast a Ball moves towards the Robot.
    If the Ball moves, but not towards the robot, the speed would be 0
    """

    def __init__(self):
        self.last_frame_time = -1
        #Time since the last video-frame was captured
        self.last_u = 0
        self.last_v = 0

    def start(self, data):
        #Initialisiere BallSpeed mit "NotFound"
        data[DATA_KEY_BALL_SPEED] = -1
        data[DATA_KEY_BALL_VECTOR] = (0, 0)

    def update(self, data):

        if DATA_KEY_CAMERA_CAPTURE_TIMESTAMP not in data:
            return

        # If no Ball is found there can't be valid data
        if not data[DATA_KEY_BALL_FOUND]:
            data[DATA_KEY_BALL_SPEED] = -1
            data[DATA_KEY_BALL_VECTOR] = (0, 0)
            self.last_frame_time = -1
            return

        if self.last_frame_time == -1:
            # wir hatten im latzen frme keinen ball
            # da wir jetzt einen haben können wir es
            # jetzt messen
            self.last_frame_time = data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP]
            self.last_u = data[DATA_KEY_BALL_INFO].u
            self.last_v = data[DATA_KEY_BALL_INFO].v
            return

        # time since last software-cycle is added to the time spent waiting for
        # a new frame as long as we do not receive a new image.
        if not data[DATA_KEY_IS_NEW_FRAME]:
            return

        # Actually it is just working while the robot is not moving
        # TODO testen obs vielleicht trotzdem geht
        if data["Walking.Active"]:
            data[DATA_KEY_BALL_SPEED] = -1
            data[DATA_KEY_BALL_VECTOR] = (0, 0)
            self.last_frame_time = -1
            return

        latest_time_frame = data[DATA_KEY_CAMERA_CAPTURE_TIMESTAMP]

        try:
            # Umwandlung von m der Distance in m/s des Ballspeeds
            delta_u = data[DATA_KEY_BALL_INFO].u - self.last_u
            delta_v = data[DATA_KEY_BALL_INFO].v - self.last_v
            # Differenzberechnung wie viel Zeit zwischen dem aktuellen und dem letzten Bild vergangen ist
            delta_timestamp = latest_time_frame - self.last_frame_time
            rolled_distance = math.sqrt(math.pow(delta_u, 2) + math.pow(delta_v, 2))
            data[DATA_KEY_BALL_SPEED] = round(rolled_distance / delta_timestamp, 5)
            data[DATA_KEY_BALL_VECTOR] = (
                delta_u / delta_timestamp,
                delta_v / delta_timestamp)
        except ZeroDivisionError:
            data[DATA_KEY_BALL_SPEED] = -1

        # Reset time after a new frame update
        self.last_frame_time = latest_time_frame
        self.last_u = data[DATA_KEY_BALL_INFO].u
        self.last_v = data[DATA_KEY_BALL_INFO].v
        debug_m(3, "Speed.delta_u", data[DATA_KEY_BALL_VECTOR][0])
        debug_m(3, "Speed.delta_v", data[DATA_KEY_BALL_VECTOR][1])
        debug_m(3, "Speed ", data[DATA_KEY_BALL_SPEED])

    def get_frame_time(self):
        return self.last_frame_time


def register(ms):
    ms.add(BallSpeedModule, "BallSpeedModule",
           requires=[DATA_KEY_IPC,
                     DATA_KEY_POSE,
                     DATA_KEY_WALKING,
                     DATA_KEY_BALL_INFO,
                     DATA_KEY_BALL_FOUND,
                     DATA_KEY_IS_NEW_FRAME],
           provides=[DATA_KEY_BALL_SPEED,
                     DATA_KEY_BALL_VECTOR])
