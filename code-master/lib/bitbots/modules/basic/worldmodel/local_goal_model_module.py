#-*- coding:utf-8 -*-
"""
TODO Das hier muss nochmal in die richtige Doku verschoben werden, weil das
hier nicht so perfekt ist

LocalGoalModelModule
^^^^^^^^^^^^^^^^^^^^

Dieses Modul stellt ein Lokales Tormodell zur verfügung.


Coordinate Systems
==================

Two coordinate systems are used. See coordinates.jpg for a visual aid.


Relative Coordinate System
--------------------------

The relative coordinate system is for local measurements of the robots. The
coordinate center is the robot, with the x axis facing forward (based on the
torso) and the y axis facing left.

Examples (unit = mm):

  * ball is 3m in front and 1m to left of robot
    => PosRel(ball) = (3000, 1000)
  * ball is 2m right to the robot
    => PosRel(ball) = (0, -2000)


Absolute Coordinate System
--------------------------

The origin of the absolute coordinate center is the center of the middle
circle (center of field). The x axis points towards the opponent goal, the
y axis to the left.::

          y
          ^       ______________________
          |     M |          |          |  O
          |     Y |_  -x, y  |  x, y   _|  P
          |     G | |        |        | |  P
     0    +     O | |       ( )       | |  G
          |     A |_|        |        |_|  O
          |     L |   -x,-y  |  x,-y    |  A
          |       |__________|__________|  L
          |
          +------------------+--------------> x
                             0

History:
''''''''

* 24.06.14: Erstellt (Nils Rokita & Marc Bestmann)

* 06.08.14 Refactor (Marc Bestmann)


"""

import time
from math import sqrt, cos, pi
import math

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.keys import DATA_KEY_GOAL_MODEL, DATA_KEY_IS_NEW_FRAME, DATA_KEY_GOAL_FOUND, DATA_KEY_GOAL_INFO, \
    DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO, DATA_KEY_IPC, BALL_INFO_FILTERED, DATA_KEY_GOAL_INFO_FILTERED
from bitbots.util.math_utils import convert_polar2uv, convert_uv2polar, convert_uv2distance
from bitbots.util.config import get_config


# noinspection PyProtectedMember
class LocalGoalModelModule(AbstractModule):
    """
    Kümmert sich um die Veränderung der Torpfostenposition durch Bewegung des
    Roboters und durch relokalisation der Tore durch die Vision
    """

    def start(self, data):
        self.goal_model = LocalGoalModel()
        self.ipc = data[DATA_KEY_IPC]
        data[DATA_KEY_GOAL_MODEL] = self.goal_model
        self.use_filtered_goals = get_config()["Toggels"]["use_filtered_goals"]

    def update(self, data):
        # u, v, angel = self.ipc.get_movement()
        # Translation und Rotation des Roboters auf die Goalposts anwenden
        # negativ anwenden weil die drehung die drehung des roboters
        # ausgleichen soll
        # self.goal_model.move(-u, -v)
        # self.goal_model.rotate(-angel)
        # falls wir neue Goal-Daten haben passen wir unsere gespeicherten
        # Werte an
        if not data[DATA_KEY_IS_NEW_FRAME]:
            return
        if data[DATA_KEY_GOAL_FOUND]:
            self.goal_model._init_correction()
            if self.use_filtered_goals:
                goal_data = data[DATA_KEY_GOAL_INFO_FILTERED]
            else:
                goal_data = data[DATA_KEY_GOAL_INFO]
            if len(goal_data) == 1:
                self.goal_model._match_one(goal_data[0])
            else:
                self.goal_model._match_two(goal_data[0], goal_data[1])
            self.goal_model._partial_remove_correction()
        # Wenn wir Informationen zum Ball haben Passen wir seine Position im
        # Modell der Realität an
        if data[DATA_KEY_BALL_FOUND]:
            self.goal_model.set_ball_position(
                data[BALL_INFO_FILTERED].u,
                data[BALL_INFO_FILTERED].v)

        debug_m(3, "EnemyGoal.centeru", self.goal_model.get_opp_goal()[0])
        debug_m(3, "EnemyGoal.centerv", self.goal_model.get_opp_goal()[1])
        debug_m(4, "EnemyGoal.post1u", self.goal_model.get_opp_goal_posts()[0][0])
        debug_m(4, "EnemyGoal.post1v", self.goal_model.get_opp_goal_posts()[0][1])
        debug_m(4, "EnemyGoal.post2u", self.goal_model.get_opp_goal_posts()[1][0])
        debug_m(4, "EnemyGoal.post2v", self.goal_model.get_opp_goal_posts()[1][1])

        debug_m(3, "OwnGoal.ucenter", self.goal_model.get_own_goal()[0])
        debug_m(3, "OwnGoal.vcenter", self.goal_model.get_own_goal()[1])
        debug_m(4, "OwnGoal.post1u", self.goal_model.get_own_goal_posts()[0][0])
        debug_m(4, "OwnGoal.post1v", self.goal_model.get_own_goal_posts()[0][1])
        debug_m(4, "OwnGoal.post2u", self.goal_model.get_own_goal_posts()[1][0])
        debug_m(4, "OwnGoal.post2v", self.goal_model.get_own_goal_posts()[1][1])




class LocalGoalModel(object):
    """
    Hält die momentane Positionen der Torpfosten for und bietet Funktionen
    zur Veränderung an
    """

    def __init__(self):
        # Pfosten 0 und 1 sind ein Tor Pfosten 2 und 3 das andere
        # Die Pfosten werden erst mit Positionen vom Mittelpunkt initalisiert
        # und relokalisieren sich dann später selbst
        self.goal_posts = []
        self.object_list = {}
        # 9000/2, 2250/2 sind die positionen vom mittelpunkt aus
        # wir verschieben das am anfang, damit wir wissen welches unser tor ist
        self.own_goal = None
        self.reset_to_own()
        self.correct_u = 0
        self.correct_v = 0
        self.correct_a = 0
        # tore in die object_list eintragen
        i = 0
        for goal_post in self.goal_posts:
            self.object_list['goal_post%d' % i] = goal_post
            i += 1

        # Ball hinzufügen
        self.object_list['ball'] = BallObject()
        self.correction_factor = 0.4  # wie schnell das modell sich ändert bei korrekturen

    def _init_correction(self):
        self.correct_u = 0
        self.correct_v = 0
        self.correct_a = 0

    def reset_to_own(self):
        # initilize with position in middle of our side
        config = get_config()['field']
        self.length = config['length']
        goal_width = config['goal-width']
        self.goal_posts.append(GoalPost(*convert_uv2polar(-self.length / 4, -goal_width / 2)))
        self.goal_posts.append(GoalPost(*convert_uv2polar(-self.length / 4, goal_width / 2)))
        self.goal_posts.append(GoalPost(*convert_uv2polar(self.length / 4 * 3, goal_width / 2)))
        self.goal_posts.append(GoalPost(*convert_uv2polar(self.length / 4 * 3, -goal_width / 2)))
        # am anfang sollte das Tor 0 unseres sein
        self.own_goal = config['own-goal']

        self.object_list['middle_point'] = LocalObject(*convert_uv2polar(self.length / 4, 0))

    def _partial_remove_correction(self):
        self.rotate((1 - self.correction_factor) * self.correct_a * (-1))
        # self.move(
        # (1-self.correction_factor) * self.correct_u * -1,
        # (1-self.correction_factor) * self.correct_v * -1)

    def move(self, u, v, correction=True):
        """
        Wendet Bewegung des Roboters auf die Position der Torpfosten an
        """
        if correction:
            self.correct_u += u
            self.correct_v += v
        for obj in self.object_list.values():
            obj.move(u, v)

    def rotate(self, angel, correction=True):
        """
        Wendet Rotationen des Roboters auf die Position der Torpfosten an
        """
        if correction:
            self.correct_a += angel
        for obj in self.object_list.values():
            obj.rotate(angel)

    def set_ball_position(self, u, v):
        """
        Setzt die Ballposition
        """
        self.object_list['ball'].set_position(u, v)

    def get_ball_position(self):
        """
        Hohlt die Ballposition im Aktuellen Modell
        """
        return self.object_list['ball'].get_uv()

    def _match_one(self, goal_info):
        """
        Findet bei nur einem sichtbaren Torpfosten heraus welche von den
        gemerkten Positionen die zugehörige ist und korrigiert diese dann
        anhand des gesehenen Torpfostens. Auch alle anderen Torpfosten
        werden um die gleichen Werte verschoben, weil unsere Odometrie
        wohl falsche Werte geliefert hat und dies betrifft dann auch die
        anderen Pfosten.
        """
        distance, angel = convert_uv2polar(goal_info.u, goal_info.v)
        if distance < 1:
            # wenn es weniger als 1mm ist wirds unten doof
            distance = 1
        min_delta = 99999999999999
        min_goal_post = None
        # hier wird der nähste Pfosten gesucht
        for goal_post in self.goal_posts:
            # abs weil floatmagie
            delta = sqrt(abs(
                distance ** 2 + goal_post.distance ** 2 -
                2 * distance * goal_post.distance * cos(angel - goal_post.angel)))
            if delta < min_delta:
                min_delta = delta
                min_goal_post = goal_post
        delta_distance = distance - min_goal_post.distance
        delta_angel = angel - min_goal_post.angel
        # jetzt werden alle Pfosten neu lokalisiert
        if delta_distance > 1000:  # todo wert evaluieren und config
            # wir rotieren nur, wenn wir weit genug weg sind
            self.rotate(self._wrap_angel(delta_angel))
        self.move(*self._calculate_move(delta_distance, min_goal_post.angel))

    def _wrap_angel(self, angel):
        return ((angel + pi) % (2 * pi)) - pi

    def _match_two(self, goal_info1, goal_info2):
        """
        Funktioniert wie match_one bloß, dass der Mittelpunkt der Tore
        genommen wird um die Verschiebung zur Odometrie zu bestimmen.
        """
        distance1, angel1 = convert_uv2polar(goal_info1.u, goal_info1.v)
        distance2, angel2 = convert_uv2polar(goal_info2.u, goal_info2.v)
        if distance1 < 1:
            # wenn es weniger als 1mm ist wirds unten doof
            distance1 = 1
        if distance2 < 1:
            # wenn es weniger als 1mm ist wirds unten doof
            distance2 = 1
        # Mittelpunkt des gesehenen Tors
        avg_distance = (distance1 + distance2) / 2
        avg_angel = (angel1 + angel2) / 2

        # Mittelpunkte der gespeicherten Tore
        avg_goal1_distance, avg_goal1_angel = self._get_goal_middel_poolar(0)
        avg_goal2_distance, avg_goal2_angel = self._get_goal_middel_poolar(1)
        # Differenz zwischen gespeicherten Toren und dem gesehen
        # abs weil float magie, machmal ist der inner ausdruck endgegend
        # der Mathematik negativ
        delta1 = sqrt(abs(
            avg_distance ** 2 + avg_goal1_distance ** 2 -
            2 * avg_distance * avg_goal1_distance * cos(avg_angel - avg_goal1_angel)))
        delta2 = sqrt(abs(
            avg_distance ** 2 + avg_goal2_distance ** 2 -
            2 * avg_distance * avg_goal2_distance * cos(avg_angel - avg_goal2_angel)))


        # entscheidung welches Tor das richtige ist
        if delta1 < delta2:
            delta_distance = avg_distance - avg_goal1_distance
            delta_angel = avg_angel - avg_goal1_angel
            goal = 0
        else:
            delta_distance = avg_distance - avg_goal2_distance
            delta_angel = avg_angel - avg_goal2_angel
            goal = 1
        # korrektur der gespeicherten Daten

        self.rotate(self._wrap_angel(delta_angel))
        self.move(*self._calculate_move(delta_distance, self._get_goal_middel_poolar(goal)[1]))

        # drehung der in sich Tore korrigieren

        # rausfinden welches das gemachte tor ist

        if delta1 < delta2:
            post1 = self.goal_posts[0]
            post2 = self.goal_posts[1]
            avg_distance, avg_angel = self._get_goal_middel_poolar(0)
        else:
            post1 = self.goal_posts[2]
            post2 = self.goal_posts[3]
            avg_distance, avg_angel = self._get_goal_middel_poolar(1)
        turnpoint_u, turnpoint_v = convert_polar2uv(avg_distance, avg_angel)
        post_u, post_v = post1.get_uv()

        # schaun welche goalinfo die richtige von dem torpfosten ist
        delta1_u = abs(post_u - goal_info1.u)
        delta1_v = abs(post_v - goal_info1.v)
        delta2_u = abs(post_u - goal_info2.u)
        delta2_v = abs(post_v - goal_info2.v)

        # drehpunkt in tor mitte verschieben
        # drehpunkt u und v

        # alle pfosten transformieren
        self.move(-turnpoint_u, -turnpoint_v, False)
        post_u, post_v = post1.get_uv()
        if delta1_u + delta1_v < delta2_u + delta2_v:
            self._correction_rotation(1, post_u, post_v, goal_info1.u - turnpoint_u, goal_info1.v - turnpoint_v)
        else:
            self._correction_rotation(1, post_u, post_v, goal_info2.u - turnpoint_u, goal_info2.v - turnpoint_v)

        # Transformation rückgängig machen
        self.move(turnpoint_u, turnpoint_v, False)

    def _correction_rotation(self, t, post_u, post_v, image_u, image_v):
        """
        Korrigiert die Drehung der beiden Tore nachdem die Tormittelpunkte korrigiert wurden.
        """
        # dreh winkel herausfinden
        post_distance, post_angel = convert_uv2polar(post_u, post_v)
        image_distance, image_angel = convert_uv2polar(image_u, image_v)
        # print image_angel, post_angel
        correction_angle = image_angel - post_angel
        # drehung durchführn
        # self.rotate(correction_angle*t, False)
        #todo this is not working???

    def _calculate_move(self, delta_distance, angel):
        """
        Berechnet die u/v verschiebung die nötig ist um die delta_distance

        an der referens von angel zu verschieben
        """
        return convert_polar2uv(delta_distance, angel)

    def _get_goal_middel_poolar(self, goal):
        """
        Gibt den Mittelpunkt eines Tores im Poolarkoordinatensystem zurück
        """
        # *2 da jedes tor aus 2 pfosten besteht
        goal *= 2
        ang = (self.goal_posts[goal].angel % (2 * pi) + self.goal_posts[goal + 1].angel % (2 * pi)) / 2
        if abs(self.goal_posts[goal].angel % (2 * pi) - self.goal_posts[goal + 1].angel % (2 * pi)) > pi:
            ang = (ang - pi) % (2 * pi)
        return ((self.goal_posts[goal].distance + self.goal_posts[goal + 1].distance) / 2,
                ang)

    def get_goals(self):
        """
        Gibt einem die Position der beiden Tore als Liste zurück
        :return: list of tupel (u,v koordinaten)
        """
        distance1, angel1 = self._get_goal_middel_poolar(0)
        distance2, angel2 = self._get_goal_middel_poolar(1)
        return [convert_polar2uv(distance1, angel1), convert_polar2uv(distance2, angel2)]

    def get_own_goal(self):
        """
        Gibt Position des eigenen Tores zurück
        """
        return convert_polar2uv(*self._get_goal_middel_poolar(self.own_goal))

    def get_own_goal_distance(self):
        return math.sqrt((self.get_own_goal()[0] ** 2) + (self.get_own_goal()[1] ** 2))

    # TODO: entbuggen
    def get_own_goal_defender_point(self):
        if self.get_own_goal_posts_distances()[0] <= self.get_own_goal_posts_distances()[1]:
            return (((self.goal_posts[0].get_uv()[0] + self.get_own_goal()[0]) / 2),
                    ((self.goal_posts[0].get_uv()[1] + self.get_own_goal()[1]) / 2))
        else:
            return (((self.goal_posts[1].get_uv()[0] + self.get_own_goal()[0]) / 2),
                    ((self.goal_posts[1].get_uv()[1] + self.get_own_goal()[1]) / 2))

    def get_opp_goal(self):
        """
        Gibt Position des gegnerischen Tores zurück
        """
        return convert_polar2uv(*self._get_goal_middel_poolar((self.own_goal + 1) % 2))

    def switch_local_goal_model_orientation(self):
        """
        Tauscht eigenes Tor und Tor des Gegners. Wird dann aufgerufen, wenn
        der Fieldie vor dem Schuss feststellt, dass das bisher angenommene
        gegnerische Tor das eigene ist.
        """
        self.own_goal = (self.own_goal + 1) % 2

    def get_goal_posts(self):
        goal_posts_uv = []
        goal_posts_uv.append(self.goal_posts[0].get_uv())
        goal_posts_uv.append(self.goal_posts[1].get_uv())
        goal_posts_uv.append(self.goal_posts[2].get_uv())
        goal_posts_uv.append(self.goal_posts[3].get_uv())
        return goal_posts_uv

    def get_own_goal_posts(self):
        goal_posts_uv = []
        goal = self.own_goal * 2
        goal_posts_uv.append(self.goal_posts[goal].get_uv())
        goal_posts_uv.append(self.goal_posts[goal + 1].get_uv())
        return goal_posts_uv

    def get_opp_goal_posts(self):
        goal_posts_uv = []
        goal = ((self.own_goal + 1) % 2) * 2
        goal_posts_uv.append(self.goal_posts[goal].get_uv())
        goal_posts_uv.append(self.goal_posts[goal + 1].get_uv())
        return goal_posts_uv

    def get_own_goal_posts_distances(self):
        own_goal_posts_distance = []
        own_goal_posts_distance.append(convert_uv2distance(self.get_goal_posts()[0][0], self.get_goal_posts()[0][1]))
        own_goal_posts_distance.append(convert_uv2distance(self.get_goal_posts()[1][0], self.get_goal_posts()[1][1]))
        return own_goal_posts_distance


    def get_opp_goal_polar(self):
        return self._get_goal_middel_poolar((self.own_goal + 1) % 2)

    def get_robot_absolute_position(self):
        #gets the absolute position of the robot and the angle to the opp goal

        #first get absolute values of x and y
        x, y = self.object_list['middle_point'].get_uv()
        x = abs(x)
        y = abs(y)
        # now decide the signs
        distance_to_opp_goal, angle_to_opp_goal = self.get_opp_goal_polar()

        # decide
        if 0 <= angle_to_opp_goal <= 180:
            #right of me -> left half
            if distance_to_opp_goal < self.length/2:
                # opp half
                # x positiv
                # y positiv
                pass
            else:
                # own half
                # x negativ
                # y positiv
                x *= -1
        elif -180 <= angle_to_opp_goal < 0:
            #left of me -> right half
            if distance_to_opp_goal < self.length/2:
                # opp half
                # x positiv
                # y negativ
                y *= -1
            else:
                # own half
                # x negativ
                # y negativ
                x *= -1
                y *= -1
        else:
            # the model is not from -180 to 180
            raise ValueError("BAM value was %f" % (angle_to_opp_goal,))

        return x, y, self.get_opp_goal_polar()[1]

class LocalObject(object):
    """
    Dieses Objekt repräsentiert ein Teil der Lokalisierung, Koordinaten werden in einem
    lokalem Polarkoordinatensystem gehalten
    """

    def __init__(self, distance, angel):
        self.distance = distance
        self.angel = angel

    def move(self, u, v):
        """
        Verschiebt die Koordinaten um u, v im Khartesischen Koordinatensystem
        """
        u1, v1 = self.get_uv()
        self.distance, self.angel = convert_uv2polar(u + u1, v + v1)

    def rotate(self, angel):
        self.angel += angel

    def get_uv(self):
        return convert_polar2uv(self.distance, self.angel)

    def get_pool(self):
        return self.distance, self.angel

    def __repr__(self):
        return "<LocalObject " + str(self.get_uv()) + " " + str(self.distance) + " " + str(self.angel) + ">"


class GoalPost(LocalObject):
    def __repr__(self):
        return "<GoalPost " + str(self.get_uv()) + " " + str(self.distance) + " " + str(self.angel) + ">"


class BallObject(LocalObject):
    def __init__(self):
        super(BallObject, self).__init__(0, 0)

    def set_position(self, u, v):
        self.distance, self.angel = convert_uv2polar(u, v)


def register(ms):
    ms.add(LocalGoalModelModule, "LocalGoalModel",
           requires=[
               DATA_KEY_IPC,
               DATA_KEY_GOAL_FOUND,
               DATA_KEY_GOAL_INFO,
               DATA_KEY_IS_NEW_FRAME,
               BALL_INFO_FILTERED,
               DATA_KEY_BALL_FOUND],
           provides=[DATA_KEY_GOAL_MODEL])
