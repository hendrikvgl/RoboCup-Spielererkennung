# -*- coding:utf-8 -*-
"""
BallModule
^^^^^^^^^^

This module takes the raw data from the vision and rates the single ballcandidates to choose one of them.
Therefor the distance and size is used.

History:
''''''''

* 28.07.17: Nils Rokita: Extraction from the VisionModule

* 06.08.14 Refactor (Marc Bestmann)
* 06.04.15 Added new filtering with rating (Marc & Nils)
* 26.04.15. Refactoring for new visualization (Marc)
"""
import time
from math import sqrt, atan, tan
import math

from bitbots.debug.debug_decorator import Debug, ComplexObjectConverter
from bitbots.debug.debuglevels import DebugLevel
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.basic.vision.vision_objects import BallInfo
from bitbots.modules.keys import DATA_KEY_RAW_BALL, DATA_KEY_TRANSFORMER, DATA_KEY_BALL_HEAD_POSE, \
    DATA_KEY_IS_NEW_FRAME, DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO, DATA_KEY_BALL_LAST_SEEN, DATA_KEY_IMAGE_POSE, DATA_KEY_CAMERA_FOOT_PHASE
from bitbots.modules.keys.visualization_keys import VIZ_KEY_VIZ_ACTIVE, VIZ_KEY_BALL_RATING_OUT, VIZ_KEY_BALL_FAR_OUT, \
    VIZ_KEY_BALL_HUGE_OUT, VIZ_KEY_BALL_SMALL_OUT, VIZ_KEY_BALL_BODY_OUT, VIZ_KEY_BALL_POSSIBLE_LIST, \
    VIZ_KEY_BEST_BALL_NUMBER
from bitbots.util import get_config


#TODO the debug output has to be rewritten, so that it is more centrelized and clean
from bitbots.util.kinematicutil import get_camera_position_p


class BallModule(AbstractModule):
    """Extrahiert den Ball aus den raw bal infos"""

    def start(self, data):
        self.transformer = data[DATA_KEY_TRANSFORMER]

        # initialisirungen
        data[DATA_KEY_BALL_FOUND] = False
        data[DATA_KEY_BALL_LAST_SEEN] = 0

        config = get_config()
        self.max_ball_distance = config["vision"]["max_distance"]
        self.ball_radius = config["vision"]["DEFAULT_RADIUS"]
        self.ball_raidus_max = config["vision"]["ball_radius_max"]
        self.ball_radius_min = config["vision"]["ball_radius_min"]
        self.cam_winkel = math.radians(config["vision"]['CameraAngle'])  # todo was 3.1
        self.ball_pos_is_ball_footpoint = config["vision"]["ball_pos_is_ball_footprint"]
        self.rating_max = config["vision"]["rating_max"]
        self.number_rated_candidates = config["vision"]["number_rated_candidates"]
        self.max_distance_to_motor = config["vision"]["max_distance_to_motor"]
        self.activate_orange_ball_hack = config["vision"]["orange_ball_hack"]

    # This decorator is scanning the data dictionary each update_time (seconds)
    # and depending on the debug level sends the defined dictionary keys as debug
    @Debug(update_time=1, list_of_data_keys={
        DebugLevel.DURING_GAME_DEBUG: [
            DATA_KEY_BALL_FOUND,
            DATA_KEY_BALL_LAST_SEEN,
        ],
        DebugLevel.GAME_PREPARE_DEBUG: [
            (DATA_KEY_BALL_INFO, ComplexObjectConverter.convert_ball_info),
        ]
    })
    def update(self, data):
        #time.sleep(0.1)
        """ Hier werden die Ballkandidaten bewertet """

        visualiization_active = data.get(VIZ_KEY_VIZ_ACTIVE, False)
        if visualiization_active:
            data[VIZ_KEY_BALL_RATING_OUT] = []
            data[VIZ_KEY_BALL_BODY_OUT] = []
            data[VIZ_KEY_BALL_SMALL_OUT] = []
            data[VIZ_KEY_BALL_HUGE_OUT] = []
            data[VIZ_KEY_BALL_FAR_OUT] = []

        if not data[DATA_KEY_IS_NEW_FRAME]:
            return
        elif data[DATA_KEY_RAW_BALL] is None:
            data[DATA_KEY_BALL_FOUND] = False
        else:
            ballinfos = []
            #iterate over all candidates
            for ball in data[DATA_KEY_RAW_BALL]:
                rating, (x, y, radius) = ball #y is the FOOT POINT of the ball in the picture

                # Sort out bad rated balls
                if rating > self.rating_max:
                    debug_m(4, "Ignore ball candidate with rating: %f" % (rating))
                    if visualiization_active:
                        data[VIZ_KEY_BALL_RATING_OUT].extend([(x, y + radius, radius, rating)])
                    continue


                # Compute distance
                (u, v) = self.transformer.transform_point_to_location(x, y, 0 if self.ball_pos_is_ball_footpoint else self.ball_radius)
                distance = sqrt(u ** 2 + v ** 2)
                if self.transformer.convex_hull([(x,y)])[0]:
                    debug_m(4, "Zu nah im Körper: konvexe Hülle")
                    #body_counter += 1
                    #data[DATA_KEY_SORTED_OUT_BALLS].extend([("B", x, y, radius)])
                    continue



                #TODO this is a hack for vision stuff with near balls. refactor. doppelung
                # For further information according to this "special ball rating" read the comments above.
                if rating == -2:
                    if self.activate_orange_ball_hack:
                        #fußpunkt zu mittelpunbkt
                        y = y + radius
                        data[DATA_KEY_BALL_FOUND] = True
                        data[DATA_KEY_BALL_INFO] = BallInfo(*[u, v, x, y, radius, rating, distance])
                        data[DATA_KEY_BALL_LAST_SEEN] = time.time()
                        debug_m(3, "BallLastSeen", data[DATA_KEY_BALL_LAST_SEEN])
                        debug_m(3, "BallFound", 1)
                        data[DATA_KEY_BALL_HEAD_POSE] = (data[DATA_KEY_IMAGE_POSE]["HeadPan"].position,
                                                         data[DATA_KEY_IMAGE_POSE]["HeadTilt"].position)
                        debug_m(2, "BallInfo", "u=%1.2f, v=%1.2f, r=%1.2f, d=%1.2f" % (u, v, distance * tan(radius*self.cam_winkel), distance))
                        return
                    else:
                        continue

                # Compute distance to our own motors, to eleminate balls on ourself
                trans_dist = self.transformer.ray_motor_distance((x, y))
                u = int(u)
                v = int(v)
                if trans_dist < self.max_distance_to_motor and u < 200 and distance < 300: #todo nich schön, hack von GO15
                    debug_m(4, "Zu nah im Körper: %f" % trans_dist)
                    if visualiization_active:
                        data[VIZ_KEY_BALL_BODY_OUT].extend([(x, y + radius, radius, trans_dist)])
                    continue

                #fußpunkt zu mittelpunkt
                y = y + radius #todo check if it is a good idea to do this, in relation to the small/huge filtering

                ballinfos.append(BallInfo(*[u, v, x, y, radius, rating, distance]))


            ball_candidate = []
            for ball in ballinfos: #todo diese schleife kann man mit der dadrüber mergen

                #todo check
                # The distance to calculate the angle the ball should cover in the picture dramatically
                # Increases when the ball is close, due to the robot's own height, this is approximated here with 320 mm
                distance = sqrt(
                        ball.distance**2 +
                        get_camera_position_p(data[DATA_KEY_TRANSFORMER].robot, data[DATA_KEY_CAMERA_FOOT_PHASE])[2]**2)

                # the radius form the vision is relative to the picture! #todo check if camera winkel is right
                radius_to_be_on_picture_max = atan(self.ball_raidus_max / distance) / self.cam_winkel #todo check if formular is correct
                radius_to_be_on_picture_min = atan(self.ball_radius_min / distance) / self.cam_winkel

                # To small
                if not radius_to_be_on_picture_min < ball.radius:
                        debug_m(3,"Ball to small. Min: %f is %f: u:%f, v:%f, r:%f" %(radius_to_be_on_picture_min, ball.radius, ball.u, ball.v, ball.rating))
                        if visualiization_active:
                            data[VIZ_KEY_BALL_SMALL_OUT].extend([(ball.x, ball.y, ball.radius, radius_to_be_on_picture_min)])
                # To huge
                elif not ball.radius < radius_to_be_on_picture_max:
                    debug_m(4,
                            "Ball to big. Max: %f is %f" % (
                                radius_to_be_on_picture_max, ball.radius))
                    if visualiization_active:
                        data[VIZ_KEY_BALL_HUGE_OUT].extend([(ball.x, ball.y, ball.radius, radius_to_be_on_picture_max)])
                else:
                    if ball.distance > self.max_ball_distance:
                        debug_m(4, "Verwerfe Balconfigl wegen großer entfernung: %f" % ball.distance)
                        if visualiization_active:
                            data[VIZ_KEY_BALL_FAR_OUT].extend([(ball.x, ball.y, ball.radius, ball.distance)])
                    else:
                        ball_candidate.append(ball)

            # check if there are sstill candidates
            if not ball_candidate:
                data[DATA_KEY_BALL_FOUND] = False
                debug_m(4, "All Ball Candidates removed in distance/Radius test")
                debug_m(3, "BallFound", 0)
                return

            # find the best ball from remaining candidates
            min_ball_delta = 999999999
            best_ball = None

            # only use the best canidates, sorted by their rating
            ball_candidate.sort(key=lambda x: x.rating)
            ball_candidate = ball_candidate[:self.number_rated_candidates]

            # for vision script debug
            if visualiization_active:
                data[VIZ_KEY_BALL_POSSIBLE_LIST] = ball_candidate

            number = 0
            best_number = -1
            # die entfernung testen
            for ball in ball_candidate:
                radius_desired = atan(self.ball_radius / ball.distance) / self.cam_winkel
                delta = abs(ball.radius - radius_desired)
                if delta < min_ball_delta:
                    min_ball_delta = delta
                    best_ball = ball
                    best_number = number
                number += 1
            # ausgewähler ball
            info = best_ball
            if visualiization_active:
                data[VIZ_KEY_BEST_BALL_NUMBER] = best_number

            data[DATA_KEY_BALL_FOUND] = True
            data[DATA_KEY_BALL_INFO] = info
            data[DATA_KEY_BALL_LAST_SEEN] = time.time()
            debug_m(3, "BallLastSeen", data[DATA_KEY_BALL_LAST_SEEN])
            debug_m(3, "BallFound", 1)
            data[DATA_KEY_BALL_HEAD_POSE] = (data[DATA_KEY_IMAGE_POSE]["HeadPan"].position,
                                             data[DATA_KEY_IMAGE_POSE]["HeadTilt"].position)
            debug_m(2, "BallInfo", "u=%1.2f, v=%1.2f, r=%1.2f, d=%1.2f" % (u, v, distance * tan(radius*self.cam_winkel), distance))


def register(ms):
    ms.add(BallModule, "Ball",
           requires=[
               DATA_KEY_RAW_BALL,
               DATA_KEY_IS_NEW_FRAME,
               DATA_KEY_TRANSFORMER,
               DATA_KEY_IMAGE_POSE,
               DATA_KEY_CAMERA_FOOT_PHASE,
               ],
           provides=[
               DATA_KEY_BALL_INFO,
               DATA_KEY_BALL_FOUND,
               DATA_KEY_BALL_LAST_SEEN,
               VIZ_KEY_BALL_RATING_OUT])
