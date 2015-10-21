#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
GoalPostModule
^^^^^^^^^^

This module takes the raw data from the vision and rates the single goalpostcandidates to choose one of them.
Therefor the distance and size is used.

History:
''''''''

* 22.04.15: Maike Paetzel, Fabian Fiedler created the module based on the ball_module
"""
import random
import time
from math import sqrt, atan, tan
import unittest
import math
from bitbots.debug.debug_decorator import Debug, ComplexObjectConverter
from bitbots.debug.debuglevels import DebugLevel

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.basic.vision.vision_objects import GoalInfo
from bitbots.modules.keys import DATA_KEY_TRANSFORMER, \
    DATA_KEY_IS_NEW_FRAME, DATA_KEY_GOAL_FOUND, DATA_KEY_GOAL_INFO, DATA_KEY_ANY_GOALPOST_LAST_SEEN, \
    DATA_KEY_RAW_GOAL_DATA
from bitbots.modules.keys.vision_keys import DATA_KEY_GOAL_INFO
from bitbots.modules.keys.visualization_keys import VIZ_KEY_SORTED_OUT_GOALS
from bitbots.util import get_config

class GoalPostModule(AbstractModule):
    """Extrahiert den Ball aus den raw bal infos"""

    def start(self, data):
        self.transformer = data[DATA_KEY_TRANSFORMER]

        # initialisirungen
        data[DATA_KEY_GOAL_FOUND] = False
        data[DATA_KEY_ANY_GOALPOST_LAST_SEEN] = 0

        config = get_config()
        self.max_goalpost_distance = config['field']['length'] + 2000 #TODO: warum plus 2000? #vlt um sicher zu sein
        self.goalpost_width = config["vision"]["GOALPOST_WIDTH"]
        self.goalpost_height = config["vision"]["GOALPOST_HEIGHT"]
        self.goalpost_width_min = config["vision"]["goalpost_width_min"]
        self.goalpost_width_max = config["vision"]["goalpost_width_max"]
        self.goalpost_height_min = config["vision"]["goalpost_height_min"]
        self.goalpost_height_max = config["vision"]["goalpost_height_max"]
        self.goal_width = config["field"]["goal-width"]
        self.goal_width_tolerance = config["vision"]["goal_width_tolerance"]
        self.cam_winkel = math.radians(config["vision"]['CameraAngle'])  # todo was 3.1
        self.focal_length = config["vision"]['FocalLength']

    # This decorator is scanning the data dictionary each update_time (seconds)
    # and depending on the debug level sends the defined dictionary keys as debug
    #@Debug(update_time=1, list_of_data_keys={
    #    DebugLevel.DURING_GAME_DEBUG: [
    #        DATA_KEY_GOAL_FOUND,
    #        DATA_KEY_ANY_GOALPOST_LAST_SEEN,
    #    ],
    #    DebugLevel.GAME_PREPARE_DEBUG: [
    #        (DATA_KEY_GOAL_INFO, ComplexObjectConverter.convert_goal_info),
    #    ]
    #})
    def update(self, data):
        #time.sleep(0.1)
        """ Hier werden die Ballkandidaten bewertet """


        if not data[DATA_KEY_IS_NEW_FRAME]:
            return
        elif data.get(DATA_KEY_RAW_GOAL_DATA, None) is None:
            data[DATA_KEY_GOAL_FOUND] = False
        else:
            goalpost_candidate = []
            goal_posts, color = data[DATA_KEY_RAW_GOAL_DATA]
            for goalpost in goal_posts:
                x, y, pixelwidth, width, height = goalpost

                (u, v) = self.transformer.transform_point_to_location(x, y, 0)

                distance = sqrt(u ** 2 + v ** 2)
                u = int(u)
                v = int(v)
                print "Höhe y:", y, " h:" , height
                print "breite x:", x, " w:",  width
                print "Dist:", distance
                print "u:", u , " v:", v


                if distance > self.max_goalpost_distance:
                    print "Entfernung Weg"
                    text = "D %.0f" % (distance)
                    data[VIZ_KEY_SORTED_OUT_GOALS].extend([(text, x, y, width, height)])
                    continue
                print " "

                width_to_be_on_picture_max = atan((self.goalpost_width_max) / distance) / (self.cam_winkel * 3/4)
                width_to_be_on_picture_min = atan((self.goalpost_width_min) / distance) / (self.cam_winkel * 3/4)
                #width_to_be_on_picture_max = self.goalpost_width_max * self.focal_length/(distance * 6)
                #width_to_be_on_picture_min = self.goalpost_width_min * self.focal_length/(distance * 6)
                print "Width max:", width_to_be_on_picture_max, "Width min:", width_to_be_on_picture_min
                #todo hier bedacht, dass der öffnungswinkel in verticaler richtung anders is als horizontal

                #heigth_to_be_on_picture_max = self.goalpost_height_max * self.focal_length/(distance * 6)
                #heigth_to_be_on_picture_min = self.goalpost_height_min * self.focal_length/(distance * 6)

                heigth_to_be_on_picture_max = atan((self.goalpost_height_max) / distance) / self.cam_winkel
                heigth_to_be_on_picture_min = atan((self.goalpost_height_min) / distance) / self.cam_winkel

                print "height max:", heigth_to_be_on_picture_max, "heit min:", heigth_to_be_on_picture_min
                print " Mittelpunkt X ist" , abs(x) + width/2
                if width_to_be_on_picture_min >= width and (abs(x) + width/2) < 0.48:
                    # Überprüfung der Breite, nur wenn Vollständig auf Bild
                    text = "WK %.0f < %.0f" % (width, width_to_be_on_picture_min)
                    data[VIZ_KEY_SORTED_OUT_GOALS].extend([(text, x, y, width, height)])
                    continue
                elif width_to_be_on_picture_max < width:
                    text = "WL %.0f > %.0f" % (width, width_to_be_on_picture_max)
                    data[VIZ_KEY_SORTED_OUT_GOALS].extend([(text, x, y, width, height)])
                    continue
                elif heigth_to_be_on_picture_min >= height and (y + height) < 0.48*3/4:
                    # Überprüfung der Höhe, nur wenn Vollständig auf Bild  TODO: Parameter evaluieren?, Da abs(x) der Mittelpunkt des Fußpunkts ist
                    text = "HK %.0f < %.0f" % (height, heigth_to_be_on_picture_min)
                    data[VIZ_KEY_SORTED_OUT_GOALS].extend([(text, x, y, width, height)])
                    continue
                elif heigth_to_be_on_picture_max < height:
                    text = "HL %.0f > %.0f" % (height, heigth_to_be_on_picture_max)
                    data[VIZ_KEY_SORTED_OUT_GOALS].extend([(text, x, y, width, height)])
                    continue
                else:
                    goalpost_candidate.append(GoalInfo(x, y, u, v, width, height))

            print "\n"

            if not goalpost_candidate:
                data[DATA_KEY_GOAL_FOUND] = False
                debug_m(4, "All Goalpost Candidates removed in distance/width and height test")
                #time.sleep(1)
                debug_m(3, "GoalFound", 0)
                return
            elif len(goalpost_candidate) == 1:
                data[DATA_KEY_GOAL_FOUND] = True
                data[DATA_KEY_GOAL_INFO] = {0: goalpost_candidate[0]}
                data[DATA_KEY_ANY_GOALPOST_LAST_SEEN] = time.time()
                data[VIZ_KEY_SORTED_OUT_GOALS].extend([("XE", goalpost_candidate[0].x, goalpost_candidate[0].y, goalpost_candidate[0].width, goalpost_candidate[0].height)])

            else:
                best_match_goal_posts = {}
                best_match_goal_value = 999999
                for i in range(len(goalpost_candidate)):
                    goalpost1 = goalpost_candidate[i]
                    for j in range(i+1, len(goalpost_candidate)):
                        goalpost2 = goalpost_candidate[j]
                        print "Pfosten1 u:", goalpost1.u, " v:", goalpost1.v, "Pfosten2 u:", goalpost2.u," v:", goalpost2.v
                        dist_posts = sqrt((goalpost1.u - goalpost2.u)**2 + (goalpost1.v - goalpost2.v)**2)
                        print "Dist:", dist_posts

                        if dist_posts >= (self.goal_width - self.goal_width_tolerance) and \
                            dist_posts <= (self.goal_width + self.goal_width_tolerance):
                            print "in Tolerance"
                            if abs(dist_posts - self.goalpost_width) < best_match_goal_value:
                                best_match_goal_posts = {0: goalpost1, 1: goalpost2} #TODO: Prüfen ob Reihenfolge relevant
                                best_match_goal_value = abs(dist_posts - self.goalpost_width)
                    if goalpost1 not in best_match_goal_posts.values():
                        print " So wir haben wegen P : ",dist_posts
                        data[VIZ_KEY_SORTED_OUT_GOALS].extend([("P", goalpost1.x, goalpost1.y, goalpost1.width, goalpost1.height)])



                if not best_match_goal_posts: #TODO Wollen wir wirklich nichts publizieren wenn wir keinen ordentlichen Match gefunden haben?
                    data[DATA_KEY_GOAL_FOUND] = False
                    debug_m(4, "All Goalpost Candidates removed in distance/width and height test")
                    #time.sleep(1)
                    debug_m(3, "GoalFound", 0)
                    return
                else:
                    data[VIZ_KEY_SORTED_OUT_GOALS].extend([("X", best_match_goal_posts[0].x, best_match_goal_posts[0].y, best_match_goal_posts[0].width, best_match_goal_posts[0].height)])
                    data[VIZ_KEY_SORTED_OUT_GOALS].extend([("X", best_match_goal_posts[1].x, best_match_goal_posts[1].y, best_match_goal_posts[1].width, best_match_goal_posts[1].height)])
                    data[DATA_KEY_GOAL_FOUND] = True
                    data[DATA_KEY_GOAL_INFO] = best_match_goal_posts
                    data[DATA_KEY_ANY_GOALPOST_LAST_SEEN] = time.time()


                    debug_m(3, "GoalLastSeen", data[DATA_KEY_ANY_GOALPOST_LAST_SEEN])
                    debug_m(3, "GoalFound", 1)
                    #TODO: GoalInfo debug Ausgabe


def register(ms):
    ms.add(GoalPostModule, "Goal",
           requires=[
               DATA_KEY_RAW_GOAL_DATA,
               DATA_KEY_IS_NEW_FRAME,
               DATA_KEY_TRANSFORMER],
           provides=[
               DATA_KEY_ANY_GOALPOST_LAST_SEEN,
               DATA_KEY_GOAL_FOUND,
               DATA_KEY_GOAL_INFO])
