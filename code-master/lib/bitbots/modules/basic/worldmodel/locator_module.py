#-*- coding:utf-8 -*-
"""
LocatorModule
^^^^^^^^^^^^^

Das Locator Module bekommt die Linieninformationen der Vision und ggf
andere Positionsinformationen und gibt eine oder mehrere mögliche
Roboterpositionen zurück

History:
''''''''

* 02.04.13 Erstellt (Robert Schmidt)

* 19.04.2014 Da der Locator nicht genutzt wird, habe ich ihn aus dem Build rausgeworfen (Robert Schmidt)

* 06.08.14 Refactor (Marc Bestmann)
"""

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
#from bitbots.locator.locator import Locator
from bitbots.locator.transformer import Transformer
from bitbots.modules.keys import DATA_KEY_IS_NEW_FRAME, DATA_KEY_GAME_STATUS, DATA_VALUE_STATE_SET, DATA_KEY_CONFIG, \
    DATA_KEY_PENALTY, DATA_KEY_TRANSFORMER, DATA_KEY_IPC, DATA_KEY_MOVING_X, DATA_KEY_IMAGE_POSE, DATA_KEY_MOVING_Y, \
    DATA_KEY_MOVING_DIRECTION, DATA_KEY_LINE_POINTS, DATA_KEY_POSITION


class LocatorModule(AbstractModule):
    """
    Das Locator Module steuert die Lokalisation des Roboters. Es bekommt
    die gesehenen Linien und Wertet sie zu einer Spielfeldposition aus.
    Diese werden getrackt.
    Die Längsachse ist x die Breitachse y
    Der Mittelpunkt hat die Koordinaten (0,0), die Einheit ist Meter
    Der Mittelpunkt des eigenen Tores hat die Position (-3, 0)
    """

    def __init__(self):
        self.last_state = None

    def start(self, data):
        # sowie ich das überblicke, muss der transformer im Python Code
        # gehalten werden, solange der C++ Teil ihn benutzt, damit die
        # Referenz beiderseitig gültig bleibt
        if DATA_KEY_TRANSFORMER in data.keys():
            self.locator = Locator(data[DATA_KEY_TRANSFORMER])
            self.transformer = data["transformer"]
            # Den alten durch den neuen Transformer in beiden Code-Teilen
            # ersetzten und den neuen behalten, damit er nicht
            # freigegeben wird
            #Der Transformer im Locator soll austauschbar sein, da die Vision
            # ihn auch benutzt für die Ballposition
            self.shared_transformer = True
        else:
            self.transformer = Transformer()
            self.transformer.set_camera_angle(data["Config"]["vision"]["CameraAngle"])
            self.locator = Locator(self.transformer)
            self.shared_transformer = False

        #Der Locator required den IPC, um das Umfallen mitzubekommen
        self.ipc = data[DATA_KEY_IPC]

        #Der Transformer Feature Toggle
        if data[DATA_KEY_CONFIG]["Toggels"]["Location"] is True:
            """ Der Feature Toggle für den Locator. Wenn die Localisation
            aktiviert sein soll, muss der Config Wert gesetzt sein. Dann
            wird update_location auf update gebunden. Somit ist die Lokalisation
            dann benutzbar. Wenn der Config-Wert false ist."""
            self.update = self.update_location

    def update(self, data):
        """ Update ist leer um den Feature Toggle für den Lokator zu
        realisieren. """
        pass

    def update_location(self, data):
        """ update_location wird durch den Toggle "Location" in der start
        dynamisch auf update gebunden."""
        if data[DATA_KEY_IS_NEW_FRAME] is False:
            return

        if data["transformerUpdated"] is False \
                or self.shared_transformer is False:
            self.transformer.update_pose(data["CameraPose"])

        x = data["Moving.X"]
        y = data["Moving.Y"]
        z = data["Moving.Direction"]
        if "LinePoints" in data.keys():
            self.evaluate_game_state(data)
            self.locator.update(data["LinePoints"], x, y, z)
            #Typ der LinePoints irgendwie überprüfen ...
            (x, y, direction) = self.locator.get_position()
            data["Position"] = (x, y, direction)
            debug_m(3, "XMoving", data["Moving.X"])
            debug_m(3, "YMoving", data["Moving.Y"])
            debug_m(3, "LinePoints", data["LinePoints"].size)

    def evaluate_game_state(self, data):
        """ Um initial zu entscheiden, ob das Verhalten Goalie ist oder
        nicht, wird der Data-Key Duty, der das Verhalten enthält genommen.
        Wenn er existiert und Goalie ist, dann wird diese Methode auf die
        Goalie-Variante gebunden, ansonsten auf die Fieldie-Variante. Der
        Fieldie ist allgemeiner, deshalb ist sie Default """
        if "Duty" in data.keys():
            if data["Duty"] == 'Goalie':
                self.evaluate_game_state = self.evaluate_game_state_goalie
            else:
                self.evaluate_game_state = self.evaluate_game_state_fieldie
        else:
            def pass_function(self, data):
                pass

            self.evaluate_game_state = pass_function

    def evaluate_game_state_goalie(self, data):
        if not self.ipc.controlable:
            self.locator.reset_position_info()

        if data.get(DATA_KEY_PENALTY):
            self.locator.say_robot_out_of_field_long_side()
            return

        if self.last_state != data[DATA_KEY_GAME_STATUS]:
            if data[DATA_KEY_GAME_STATUS] == DATA_VALUE_STATE_SET:
                self.locator.say_robot_is_goalie()

    def evaluate_game_state_fieldie(self, data):
        if not self.ipc.controlable:
            self.locator.reset_position_info()

        if data.get(DATA_KEY_PENALTY):
            self.locator.say_robot_out_of_field_long_side()
            return

        if self.last_state != data[DATA_KEY_GAME_STATUS]:
            if data[DATA_KEY_GAME_STATUS] == DATA_VALUE_STATE_SET:
                self.locator.say_robot_in_own_half()


def register(ms):
    ms.add(LocatorModule, "Locator",
           requires=[
               DATA_KEY_IMAGE_POSE,
               DATA_KEY_MOVING_X,
               DATA_KEY_MOVING_Y,
               DATA_KEY_MOVING_DIRECTION,
               DATA_KEY_LINE_POINTS,
               DATA_KEY_CONFIG,
               DATA_KEY_GAME_STATUS,
               DATA_KEY_PENALTY,
               DATA_KEY_IPC],
           #, "Duty"
           provides=[DATA_KEY_POSITION])

#Das Requirement Behavior noch einmal überdenken, da der Locator es nur einmal zur Bestimmung nutzt, ob er ein Goalie ist.
#Das Weltmodell ist auch noch nicht auf Selbstständigkeit aus
