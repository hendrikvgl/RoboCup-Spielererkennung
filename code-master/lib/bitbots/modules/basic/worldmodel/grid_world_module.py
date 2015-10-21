# coding=utf-8
"""
GridWorldModule
^^^^^^^^^^^^^^^

The grid world module can calculate the own position and the position of opponent robots and the stores this data
in the grid world. The grid world divides the field in a certain amount of cells and then stores if there's
anything in these cells, for example a team mate or an opponent.
This data is also shared with other robots so every team member can benefit from it.
The origin of the grid world is at the mid point of the field.

Meaning of the numbers stored in the grid (Some of them are not used yet):

0: Nothing
1: Own goal
2: Opponent's goal
3: Own position
4: Team member
5: Opponent
6: General obstacle
7: Ball

History:
''''''''

* ??.12.14: Created (Benjamin Scholz)
"""
from bitbots.modules.keys.grid_world_keys import DATA_KEY_OPPONENT_ROBOT, DATA_KEY_TEAM_MATE, DATA_KEY_OWN_POSITION_GRID
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_GOAL_FOUND, DATA_KEY_GOAL_INFO_FILTERED, \
    DATA_KEY_IS_NEW_FRAME, DATA_KEY_HORIZON_OBSTACLES, DATA_KEY_OBSTACLE_FOUND
from bitbots.util.config import get_config

import math
import numpy as np
import time
import Queue


class GridWorldModule(AbstractModule):
    """
    grid world module class
    """
    def start(self, data):
        """
        Starting the grid world module, setting a variables like the amount of cells, initializing the grid
        :param data: BitBots data object
        """
        # letzter Start
        self.lastStart = time.time()

        self.grid = dict()
        config = get_config()['field']
        self.length = config['length']
        self.width = config['width']
        self.goal_width = config['goal-width']

        # Cells
        self.xCount = 19  # Amount of cells in horizontal direction
        self.yCount = 13  # Amount of cells in vertical direction
        self.cellCount = self.yCount * self.xCount

        self.x_half = int(self.xCount / 2)
        self.y_half = int(self.yCount / 2)
        self.initialize_grid()

        # Ist -1 wenn der Roboter auf das eigene Tor guckt und 1 wenn er auf das gegnerische Tor guckt
        # Zu Beginn ist der Wert 1, da wir davon ausgehen,
        # dass der Roboter zum Start immer auf das gegnerische Tor guckt
        # Bisher ist jedoch noch keine Loesung dafuer implementiert, um festzustellen auf welches Tor
        # der Roboter schaut.
        self.field_half = 1

        # bin_tm und bin_opp speichern die Binaerrepraesentation der Gridworld
        # und werden zunaechst auf einen default-Wert gesetzt bis es Daten gibt,
        # die eingetragen werden koennen. Die DATA_KEYs werden in update mit ihnen verglichen,
        # damit einige Operationen nur durchgefuehrt werden, wenn sich die Daten tatsaechlich
        # geaendert haben.
        self.bin_tm = [999999, 999999, 999999, 999999, 999999, 999999, 999999, 999999]
        self.bin_opp = [999999, 999999, 999999, 999999, 999999, 999999, 999999, 999999]

    def initialize_grid(self):
        """
        Initialses the grid world with a certain amount of cells and sets every cell at the beginning to zero, meaning
        there's nothing in this cell yet.
        """
        for i in range(-self.x_half, self.x_half+1):
            for j in range(-self.y_half, self.y_half+1):
                self.grid[(i, j)] = 0

        # Setzen der Tore
        owngoal_x, owngoal_y = self.get_goal("own")
        enemygoal_x, enemygoal_y = self.get_goal("enemy")

        self.set_position(owngoal_x, owngoal_y, 1)
        self.set_position(enemygoal_x, enemygoal_y, 2)

    def update(self, data):
        """
        update method.
        :param data: BitBots data object
        """
        # Wenn es noch keinen neuen Frame gibt, dann wird update nicht ausgefuehrt
        if not data[DATA_KEY_IS_NEW_FRAME]:
            return

        # Maximal 1x pro Sekunde das Skript aufrufen
        if not self.lastStart < time.time() - 1:
            return

        # Letzten Start (Skriptausführung) updaten
        self.lastStart = time.time()

        # Es wird ueberprueft, ob ein Team-Kollege Daten gesendet hat.
        bin_opp = \
            data.get(DATA_KEY_OPPONENT_ROBOT, [999999, 999999, 999999, 999999, 999999, 999999, 999999, 999999])
        if self.bin_opp != bin_opp:
            # print("DataKeyOpponent: " + str(self.bin_opp))
            # Falls tatsaechlich etwas gesendet wurde, dann weicht es vom default-Wert ab und wird ins Grid eingetragen
            if 999999 not in bin_opp:
                self.bin_opp = bin_opp[:]
                self.binary_to_grid(bin_opp, 5)

        bin_tm = \
            data.get(DATA_KEY_TEAM_MATE, [999999, 999999, 999999, 999999, 999999, 999999, 999999, 999999])
        if self.bin_tm != bin_tm:
            # print("DataKeyTeamMate: " + str(self.bin_tm))
            if 999999 not in self.bin_tm:
                self.bin_tm = bin_tm[:]
                self.binary_to_grid(bin_tm, 4)
        # print("DataKeyTeamMate: " + str(bin_tm))
        # Falls tatsaechlich etwas gesendet wurde, dann weicht es vom default-Wert ab und wird ins Grid eingetragen
        if 999999 not in bin_tm:
            self.binary_to_grid(bin_tm, 4)

        # Falls der Roboter ein Tor sieht, dann kann er seine eigene Position bestimmen
        if not (math.isnan(data[DATA_KEY_GOAL_INFO_FILTERED].u_center)
                and math.isnan(data[DATA_KEY_GOAL_INFO_FILTERED].v_center)):
            self.set_own_position_vector(data)

        # Falls der Roboter einen Gegner sieht, dann kann er dessen Position bestimmen
        if data[DATA_KEY_OBSTACLE_FOUND]:
            obstaclelist = data[DATA_KEY_HORIZON_OBSTACLES]
            self.set_opponent_position(data, obstaclelist)

        # Debugging Zeugs
        #self.printgrid()

    def get_goal(self, side):
        """
        Returns a goal's position on the field in grid coordinates.
        :param side: "own" or "enemy" depending on the goal's position you need
        :type side: str
        :return: the centre of the goal as x- and y-values for the grid
        :rtype: int, int
        """
        if side == "own":
            return -self.x_half, 0
        elif side == "enemy":
            return self.x_half, 0
        else:
            return "fehler"

    def in_field(self, x, y):
        """
        Checks if a certain position exists in the grid world
        :param x: x-value for the grid world
        :type x: int
        :param y: y-value for the grid
        :type y: int
        :return: True if the position exists in the grid world, False if not
        :rtype: bool
        """
        if -self.x_half < x < self.x_half and -self.y_half < y < self.y_half:
            return True
        else:
            return False

    def get_around_position(self, x, y, typ):
        """
        Checks if there's a certain value present around a given position in the grid world
        :param x: x position in the grid
        :type x: int
        :param y: y-position in the grid
        :type y: int
        :param typ: what type is the method supposed to check for in the grid
        :type typ: int
        :return: positions around x- and v-value the given type is present
        :rtype: list
        """

        x = int(x)
        y = int(y)
        positions = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if self.in_field(i, j) and (x, y) != (i, j):
                    if self.grid[(i, j)] == typ:
                        positions.append([i, j])
        return positions

    def grid_to_binary(self, typ):
        """
        Converts the grid into the binary representation, that is needed to send the grid over the mitecom.
        But this representation can only store one type.
        :param typ: is it a team mate, opponent or...
        :type typ: list
        :return: A list of integers, each representing one part of the field
        :rtype: list
        """

        # position ist die Position der Zelle angefangen bei 0
        position = 0

        # rechnet aus wie viele 32 bit integer verwendet werden
        integercount = int(math.ceil(self.cellCount/32.0))

        # binarylist ist eine Liste der Integer, die das Grid repraesentieren. Zunaechst sind diese alle 0
        binarylist = [0] * integercount

        # listcount gibt an welcher Integer gerade fuer den Abschnitt im Grid zustaendig ist
        listcount = 0

        for i in range(-self.x_half, self.x_half+1):
            for j in range(-self.y_half, self.y_half+1):
                if self.grid[(i, j)] in typ:
                    binarylist[listcount] += 2**(position % 32)
                position += 1
                # Bei jeder 32. position wird der listcount um einen erhoeht, da nur 32 bit Integer verwendet werden
                if position % 32 == 0:
                    listcount += 1
        return binarylist

    def bitfield(self, n):
        """
        Converts an integer into a binary number. The binary number is reversed for easier handling in for-loops.
        :param n: Part of the grid as integer
        :type n: int
        :return: Part of the grid in binary representation. The binary number is reversed.
        :rtype: str
        """
        num = bin(n)[2:]           # Konvertiert n in z.B. den String 0b101, [2:] löscht '0b'
        num = num.rjust(32, "0")   # String auf 32 Stellen links mit Nullen auffüllen und zurückgeben
        return num[-1::-1]         # String umdrehen, um zahl einfacher in for-schleifen nutzen zu koennen

    def binary_to_grid(self, binarylist, typ):
        """
        Enters the given binary representation of the grid into the grid world.
        :param binarylist: list of integers that each represent one part of the field
        :type binarylist: list of int
        :param typ: Sind die Werte Mitspieler, Gegner oder...
        :type typ: int
        """
        position = 0
        listcount = 0
        for i in range(-self.x_half, self.x_half+1):
            for j in range(-self.y_half, self.y_half+1):
                if position % 32 == 0:
                    bin_str = self.bitfield(binarylist[listcount])
                    listcount += 1
                # Teammates ueberschreiben die eigene Position nicht und Gegner ueberschreiben Teammates nicht
                if bin_str[position % 32] == "1" and not self.grid[(i, j)] == 3:
                    if not(typ == 5 and self.grid[(i, j)] == 4):
                        self.grid[(i, j)] = typ
                # Ist eine Position fuer den Teammate in der gesendeten Grid-World nicht mehr enthalten,
                # dann wird diese geloescht.
                if bin_str[position % 32] == 0 and typ == 4 and self.grid[(i, j)] == 4:
                    self.grid[(i, j)] = 0
                position += 1

    def get_goal_width(self, data):
        """
        Calculates the goal width with the u- and v-values the robot has for the posts.
        :param data: provides data keys
        :return: the goal width
        :rtype: float
        """
        # if not (type(vektor1) == np.ndarray) or not (type(vektor2) == np.ndarray):
        #     raise Exception("Parameter muessen ein numpy-Array sein.")
        # Voraussetzung ist, dass 0 der linke und 1 der rechte Pfosten ist.
        u1 = data[DATA_KEY_GOAL_INFO_FILTERED].u_post1
        v1 = data[DATA_KEY_GOAL_INFO_FILTERED].v_post1
        u2 = data[DATA_KEY_GOAL_INFO_FILTERED].u_post2
        v2 = data[DATA_KEY_GOAL_INFO_FILTERED].v_post2

        # Sollten die u und v Werte nicht gesetzt sein, dann wird die festgelegte Breite zurueckgegeben
        if u1 == 0 or u2 == 0 or v1 == 0 or v2 == 0:
            return self.goal_width

        # Die u und v Werte werden in die Längen des Grids umgewandelt, für weitere Berechnungen
        u1 = self.__giveFloatNotNull(u1)
        u2 = self.__giveFloatNotNull(u2)
        v1 = self.__giveFloatNotNull(v1)
        v2 = self.__giveFloatNotNull(v2)

        # Erstellen von 2 Vektoren zur Berechnung der vom Roboter gesehenen Breite des Tores
        vektor1 = np.array([[u1, v1]]).T
        vektor2 = np.array([[u2, v2]]).T

        vektor_diff = vektor1 - vektor2
        goal_width = math.sqrt(vektor_diff[0, 0]**2 + vektor_diff[1, 0]**2)

        return goal_width

    def get_pos_state(self, x, y):
        """
        Returns the content of a given position in the grid.
        :param x: x-value in the grid
        :type x: int
        :param y: y-value in the grid
        :type y: int
        :return: value for the given position
        :rtype: int
        """
        return self.grid.get((x, y))

    def get_pos(self, typ):
        """
        returns a list of positions from the grid world for a given type
        :param typ: is it a team mate, opponent or...
        :type typ: int
        :return: The found positions as a list
        :rtype: list
        """
        positions = []
        for key in self.grid:
            if self.grid[key] == typ:
                positions.append(key)
        return positions

    def get_own_pos(self):
        """
        returns the position of the robot
        :return: True if there is a position for the robot in the grid world, also the x- and y-coordinates
        :rtype: bool, int, int
        """
        for key in self.grid:
            if self.grid[key] == 3:
                return True, key[0], key[1]
        return False, 0, 0

    def set_position(self, x, y, new_position):
        """
        sets a given number at a given position in the grid world
        :param x: x-position in the grid
        :type x: int
        :param y: y-position in the grid
        :type y: int
        :param new_position: the value that is supposed to be set at the given position
        :type new_position: int
        """
        if self.in_field(x, y):
            self.grid[(x, y)] = new_position

    def uv_to_coordinates(self, u, v):
        """
        converts u- and v-values form millimetre to amount of cells in the grid world
        :param u: distance in front of the robot in millimetre
        :type u: float
        :param v: distance to the left of the robot in millimetre
        :type v: float
        :return: x- and y-values
        :rtype: float
        """
        x = (u / self.length) * self.xCount
        y = (v / self.width) * self.yCount
        return x, y

    def angle_posts(self, data):
        """
        calculates the angles between the right and left goal post and lines that are the direct distances between the
        robot and the goal posts.
        :param data: provides data keys
        :return: The angles between the goal posts and direct distances from the robot to the posts in radians.
        :rtype: float, float
        """
        # Voraussetzung ist, dass 0 der linke und 1 der rechte Pfosten ist.
        u1 = data[DATA_KEY_GOAL_INFO_FILTERED].u_post1
        v1 = data[DATA_KEY_GOAL_INFO_FILTERED].v_post1
        u2 = data[DATA_KEY_GOAL_INFO_FILTERED].u_post2
        v2 = data[DATA_KEY_GOAL_INFO_FILTERED].v_post2

        if u1 == 0 or u2 == 0 or v1 == 0 or v2 == 0:
            return 0, 0

        # Die u und v Werte werden in die Längen des Grids umgewandelt, für weitere Berechnungen
        u1 = self.__giveFloatNotNull(u1)
        u2 = self.__giveFloatNotNull(u2)
        v1 = self.__giveFloatNotNull(v1)
        v2 = self.__giveFloatNotNull(v2)

        # Die Abstände zu den Pfosten werden berechnet
        c1 = math.sqrt(u1 ** 2 + v1 ** 2)
        c1 = self.__giveFloatNotNull(c1)
        c2 = math.sqrt(u2 ** 2 + v2 ** 2)
        c2 = self.__giveFloatNotNull(c2)

        goal_width = self.get_goal_width(data)

        angle_right = math.acos((c1 ** 2 - c2 ** 2 - goal_width ** 2) / (-2 * c2 * goal_width))
        angle_left = math.acos((c2 ** 2 - c1 ** 2 - goal_width ** 2) / (-2 * c1 * goal_width))

        return angle_left, angle_right

    def __giveFloatNotNull(self, param):
        """
        Checks if a given parameter is either None or 0 and in that case returns 0.01.
        :param param: can be anything
        :return: either the given parameter or 0.01
        """
        if (param is None) or (param == 0):
            param = 0.01

        return param

    def set_own_position_vector(self, data):
        """
        Calculates the own positition of the robot in the grid with the usage of vectors.
        :param data: provides data keys
        """
        # Berechnen der benötigten verktoren
        u = data[DATA_KEY_GOAL_INFO_FILTERED].u_center
        v = data[DATA_KEY_GOAL_INFO_FILTERED].v_center
        mid_to_goal_vector = self.field_half * np.array([[self.length/2.0, 0]]).T
        robot_to_goal_vector = self.field_half * np.array([[u, v]]).T

        # Multiplikation mit Rotationsmatrix, um den Vektor des Roboters zum Tor auf das Koordinatensystem
        # des Grids anzupassen.
        angle_to_grid = self.get_angle_to_grid(data)
        rotation_matrix = np.array([[np.cos(angle_to_grid), -np.sin(angle_to_grid)], [np.sin(angle_to_grid), np.cos(angle_to_grid)]])
        robot_to_goal_vector_corr = rotation_matrix * robot_to_goal_vector

        # Vektorrechnung: c = a - b
        # Wobei a = mid_to_goal_vector, b = robot_to_goal_vector und c = mid_to_robot_vector
        # Aufgrund der Vektor-Subtraktion stellt die Differenz aus den beiden Vektoren a und b
        # die absolute Positon des Roboters auf dem Feld (c) dar
        mid_to_robot_vector = mid_to_goal_vector - robot_to_goal_vector_corr

        x_pos = mid_to_robot_vector[0, 0] / self.length * self.xCount
        y_pos = mid_to_robot_vector[1, 0] / self.width * self.yCount

        # Runden der Ergebnisse, da das Grid nur Integer-Werte annimmt
        x_pos = round(x_pos)
        y_pos = round(y_pos)

        # Zunächst muss der alte Wert gelöscht werden
        is_set, x_old, y_old = self.get_own_pos()

        if is_set and (x_pos != x_old or y_pos != y_old):
            self.set_position(x_old, y_old, 0)

        # neuer Wert wird geschrieben
        self.set_position(x_pos, y_pos, 3)
        bin_tm = self.grid_to_binary([3, 4])
        data[DATA_KEY_TEAM_MATE] = tuple(bin_tm)

    def set_own_position_goal_posts(self, data):
        """
        Calculates the position of the robot with the usage of angles.
        :param data: provides data keys
        """
        half_goal_width = self.get_goal_width(data) / 2.0

        angle_left, angle_right = self.angle_posts(data)
        #print "left" + str(angle_left) + "right" + str(angle_right)
        if angle_left == 0 and angle_right == 0 or math.isnan(angle_left) or math.isnan(angle_right):
            return

        # Berechnung der Steigung der beiden Geraden von den Pfosten zum Roboter
        slope_left = -1*(1 / math.tan(math.radians((180.0 - math.degrees(angle_left)))))
        slope_right = -1*(1 / math.tan(angle_right))

        # Berechnene des Schnittpunktes der beiden Geraden
        # Funktion 1: Y=slope_left*x+b1
        # Funktion 2: Y=slope_right*x+b2
        # Gesucht: b1 und b2

        b1 = half_goal_width - (slope_left * (self.length / 2.0))
        b2 = - half_goal_width - (slope_right * (self.length / 2.0))



        # Nun da wir die Funktionen komplett haben, kann der Schnittpunkt berechnet werden
        inter_x = (b2 - b1) / (slope_left - slope_right)
        inter_y = slope_left * inter_x + b1
        #print "interx" + str(inter_x) + "intery" + str(inter_y)


        # Die Werte werden von mm in die Groessen der Grid-World umgewandelt
        inter_x = (inter_x / self.length) * self.xCount
        inter_y = (inter_y / self.width) * self.yCount

        # Runden der Ergebnisse, da das Grid nur Integer-Werte annimmt
        x_pos = int(round(inter_x))
        y_pos = int(round(inter_y))

        # Die Werte x_pos und y_pos werden angepasst je nachdem auf welcher Haelfte des Feldes der Roboter steht
        x_pos *= self.field_half
        y_pos *= self.field_half


        #print "x" + str(x_pos) + "y" + str(y_pos)

        # Prueft ob die gefundene Position innerhalb des Grids ist und bricht ab falls nicht.
        if not self.in_field(x_pos, y_pos):
            return

        # Zunächst muss der alte Wert gelöscht werden
        is_set, x_old, y_old = self.get_own_pos()

        if is_set and (x_pos != x_old or y_pos != y_old):
            self.set_position(x_old, y_old, 0)

        self.set_position(x_pos, y_pos, 3)
        bin_tm = self.grid_to_binary([3, 4])
        data[DATA_KEY_TEAM_MATE] = tuple(bin_tm)

    def get_angle_to_grid(self, data):
        """
        Calculates the angle from the robot to the x-axis of the grid
        :param data: provides data keys
        :return: the angle of the robot to the x-axis of the grid in degrees
        :rtype: float
        """

        # Werte für Pfosten 1 und Pfosten 2
        u1 = data[DATA_KEY_GOAL_INFO_FILTERED].u_post1
        v1 = data[DATA_KEY_GOAL_INFO_FILTERED].v_post1
        u2 = data[DATA_KEY_GOAL_INFO_FILTERED].u_post2
        v2 = data[DATA_KEY_GOAL_INFO_FILTERED].v_post2

        if u1 == 0 or u2 == 0 or v1 == 0 or v2 == 0:
            return 999

        c1 = math.sqrt(u1 ** 2 + v1 ** 2)
        c2 = math.sqrt(u2 ** 2 + v2 ** 2)

        # Winkel vom Roboter zum Tor berechnen
        sinbeta1 = v1 / c1
        sinbeta2 = v2 / c2
        beta1 = math.degrees(math.asin(sinbeta1))
        beta2 = math.degrees(math.asin(sinbeta2))

        # Winkel vom Tor zum Grid berechnen
        angle_left, angle_right = self.angle_posts(data)
        if angle_left == 0 and angle_right == 0:
            return 999
        angle_left = math.degrees(angle_left)
        angle_right = math.degrees(angle_right)
        new_angle_left = abs(90 - angle_left)
        new_angle_right = abs(90 - angle_right)

        # Berechnung des Winkels vom Roboter zum Grid.
        # Dazu wrid der Winkel vom Roboter zum Tor und wiederum der Winkel vom Tor zum Grid verwendet
        if u2 > u1:
            angle = 360 - new_angle_right + beta2
        else:
            angle = beta1 + new_angle_left

        # Die Berechnung geht davon aus, dass wir auf das gegnerische Tor schauen. Daher muessen wir den Wert
        # anpassen, falls wir auf das eigene Tor schauen.
        if self.field_half == -1:
            angle = (angle + 180) % 360
        #print "angle: " + str(angle)
        return angle

    def set_opponent_position(self, data, obstaclelist):
        """
        Enters found opponents onto their positions in the grid world
        :param data: provides data keys
        :param obstaclelist: list of u- and v-values of obstacles
        :type obstaclelist: list
        """
        is_set, x1, y1 = self.get_own_pos()
        if is_set:
            for u, v in obstaclelist:
                distance = math.sqrt(u ** 2 + v ** 2)
                # Winkel vom Roboter zum Objekt
                angle_to_grid = self.get_angle_to_grid(data)
                if angle_to_grid == 999 or u == 0 or v == 0 or math.isnan(angle_to_grid) or math.isnan(u) or math.isnan(v):
                    return
                angle_to_object = math.degrees(math.acos((u ** 2 - v ** 2 - distance ** 2) / (-2 * abs(v) * distance)))
                if v < 0:
                    angle_object_to_grid = (angle_to_grid - angle_to_object) % 360
                else:
                    angle_object_to_grid = (angle_to_grid + angle_to_object) % 360

                u2 = distance * math.cos(math.radians(angle_object_to_grid))
                v2 = distance * math.sin(math.radians(angle_object_to_grid))
                x2, y2 = self.uv_to_coordinates(u2, v2)
                obj_x = int(round(x1 + x2))
                obj_y = int(round(y1 + y2))
                # old_typ ist der Wert der vorher an der Position im Grid eingetragen war.
                old_typ = self.get_pos_state(obj_x, obj_y)
                # Die Gegner werden nur eingetragen, wenn auf der Position nicht bereits entweder
                # ein Teammate oder die eigene Position eingetragen ist.
                # Es wird ausserdem geprueft ob die Position ueberhaupt noch im Feld ist.
                if old_typ != 3 and old_typ != 4 and old_typ != 5 and self.in_field(obj_x, obj_y):
                    self.set_position(obj_x, obj_y, 5)
                    around_pos = self.get_around_position(obj_x, obj_y, 5)

                    # pruefen ob um die neue Position des Gegners alte Positionen von Gegnern sind.
                    # Falls ja und der Roboter diese nicht in seiner Liste hat, dann werden diese
                    # Positionen auf 0 gesetzt.
                    for pos in around_pos:
                        if pos not in obstaclelist:
                            self.set_position(pos[0], pos[1], 0)
            bin_opp = self.grid_to_binary([5])
            data[DATA_KEY_OPPONENT_ROBOT] = tuple(bin_opp)

    def find_best_path(self, start, goal):
        """
        finds a path in grid from one point to another, by using the A* search algorithm. The path avoids obstacles
        like team members or opponents. This code hasn't been tested yet.
        :param start: the start position as x- and y-values for the grid
        :type start: (int, int)
        :param goal: the end position as x- and y-values for the grid
        :type goal: (int, int)
        :return: path as a list of positions the robot has to walk along to reach the goal
        :rtype: list
        """
        closed = set([])
        fringe = Queue.PriorityQueue(0)
        distance = self.manhattandistance(start, goal)
        fringe.put((distance, [], start))
        while not fringe.empty():
            distance, path, position = fringe.get()
            if position == goal:
                return path
            if position not in closed:
                closed.add(position)
                successors = self.getsuccessors(position)
                for x, y in successors:
                    mandistance = self.manhattandistance((x, y), goal)
                    newpath = path[:]
                    newdistance = len(newpath) + mandistance
                    newpath.append((x, y))
                    fringe.put((newdistance, newpath, (x, y)))
        return []

    def getsuccessors(self, position):
        """
        finds the next positions the robot can go to from a given position. Meaning there is no other object in
        these positions at the time. This code hasn't been tested yet.
        :param position: x- and y-values for the grid
        :type position: (int, int)
        :return:a list of possible next positions
        :rtype: list
        """
        x, y = position
        successors = []
        for i in range(x - 1, x + 2):
            if self.get_pos_state(i, y) == 0 and (x, y) != (i, y):
                successors.append((i, y))
        for i in range(y - 1, y + 2):
            if self.get_pos_state(x, i) == 0 and (x, y) != (x, i):
                successors.append((x, i))
        return successors

    def manhattandistance(self, point1, point2):
        """
        calculates the manhattan distance from one point on the grid to the other.
        :param point1: a position in the grid world
        :type point1: (int, int)
        :param point2: another position in the grid world
        :type point2: (int, int)
        :return: the manhattan distance between the two points
        :rtype: int
        """
        x, y = point1
        x2, y2 = point2
        distance = abs(x - x2) + abs(y - y2)
        return distance

    def responsible(self, point):
        """
        calculates if this robot is closer than all his team members to a certain point on the field by using the
        manhattan distance. This code hasn't been tested yet.
        :param point: x- and y-coordinates for the grid
        :type point: (int, int)
        :return: True if the robot is the closest and False if the robot isn't
        :rtype: bool
        """
        own_pos = self.get_own_pos()
        own_distance = self.manhattandistance(own_pos[1:], point)
        teammates = self.get_pos(4)
        for i in teammates:
            distance = self.manhattandistance(i, point)
            if own_distance > distance:
                return False
        return True

    def printgrid(self):
        """
        prints the grid to the terminal.
        """
        grid = ""
        grid += "=============================================================\n"
        grid += "    "  # spacer
        for i in range(-self.x_half, self.x_half+1):
            grid += str(i).rjust(2, " ") + " "
        grid += "\n"

        for j in range(-self.y_half, self.y_half+1):
            grid += str(j).rjust(2, " ") + ": "
            for i in range(-self.x_half, self.x_half+1):
                grid += str(self.grid[(i, j)]).rjust(2, " ") + " "
                if i == self.x_half:
                    grid += "\n"
        grid += "\n"
        print grid


def register(ms):
    ms.add(GridWorldModule, "GridWorld",
           requires=[
               DATA_KEY_GOAL_FOUND,
               DATA_KEY_GOAL_INFO_FILTERED,
               DATA_KEY_IS_NEW_FRAME,
               DATA_KEY_HORIZON_OBSTACLES],
           provides=[
               DATA_KEY_OPPONENT_ROBOT,
               DATA_KEY_TEAM_MATE,
               DATA_KEY_OWN_POSITION_GRID])
