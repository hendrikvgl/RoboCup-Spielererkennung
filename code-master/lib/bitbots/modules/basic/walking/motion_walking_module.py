#-*- coding:utf-8 -*-
"""
MotionWalkingModule
^^^^^^^^^^^^^^^^^^^

Das WalkingModule kümmert sich um die ansteuerung und Parametresierung
der Walkingengine. Dabei sorgt sie dafür das es nach möglichkeit nicht
zu zu heftigen Änderungen und Werten kommt.

Diese Spezielle ausprägung gibt die Werte an eine innerhalb der Motion
Laufende Walkinginstanz durch

History:
''''''''

* 29.01.14: Erstellt (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

* 15.04.15 Die Berechnung der Maximalen Beschleunigung Refactored (Fabian Fiedler)


"""
import time

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.keys import DATA_VALUE_STATE_PLAYING, DATA_KEY_GAME_STATUS, DATA_KEY_CONFIG, DATA_KEY_IPC, \
     DATA_KEY_WALKING, DATA_KEY_MOTION_WALKING, DATA_KEY_WALKING_HIP_PITCH_OUT, DATA_KEY_WALKING_FORWARD, \
    DATA_KEY_WALKING_SIDEWARD, DATA_KEY_WALKING_ANGULAR, DATA_KEY_WALKING_FORWARD_REAL, DATA_KEY_WALKING_SIDEWARD_REAL, \
    DATA_KEY_WALKING_ANGULAR_REAL, DATA_KEY_WALKING_ACTIVE, DATA_KEY_WALKING_RUNNING, DATA_KEY_WALKING_ARMS
from bitbots.ipc import STATE_WALKING

from numpy import sign

class MotionWalkingModule(AbstractModule):
    """
    Das Walking Module läuft als eigener Process um etwas rechenlast auf
    einen anderen Prozessorkern zu verlagern, und um möglichst
    unabhängig von den anderen Modulen zu sein, da schon leichte
    verzögerungen in den berechnungen des Walkings schnell zum umfallen
    beim laufen führen. Es eignet sich recht gut für einen eigenen
    Prozess da nur wenige Daten übertragen werden müssen und die nicht
    wirklich geschwindigkeitskritisch sind (das beendenn eines Schrittes
    dauert sowieso mehrere Sekunden da sind einige ms egal).
    """

    def start(self, data):
        """
        Ließt einige werte aus der Config, und setzt die Startparameter
        """
        #arme am anfang richtig setzen, bevor multithreading das kaputt
        #macht
        config = data[DATA_KEY_CONFIG]
        data[DATA_KEY_WALKING_HIP_PITCH_OUT] = config["ZMPConfig"][config["RobotTypeName"]]["HipPitch"]
        data[DATA_KEY_WALKING_FORWARD] = 0
        data[DATA_KEY_WALKING_SIDEWARD] = 0
        data[DATA_KEY_WALKING_ANGULAR] = 0
        data[DATA_KEY_WALKING_FORWARD_REAL] = 0
        data[DATA_KEY_WALKING_SIDEWARD_REAL] = 0
        data[DATA_KEY_WALKING_ANGULAR_REAL] = 0
        data[DATA_KEY_WALKING_ACTIVE] = False
        data[DATA_KEY_WALKING_RUNNING] = False
        data[DATA_KEY_WALKING_ARMS] = True
        data[DATA_KEY_WALKING_ARMS] = not data[DATA_KEY_CONFIG]["walking.armsOff"]

        self.ipc = data[DATA_KEY_IPC]
        self.config = config['ZMPConfig'][config["RobotTypeName"]]

        self.lastforward = 0
        self.lastsideward = 0
        self.lastangular = 0
        self.updateslower = time.time()
        self.angularfaktor = 5 #TODO Config?

        self.log_counter = 0

        self.max_forward_speed = self.config["MAX_FORWARD_SPEED"]
        self.max_sidewards_speed = self.config["MAX_SIDEWARDS_SPEED"]
        self.max_angular_speed = self.config["MAX_ANGULAR_SPEED"]
        self.speed_delta = self.config["SPEED_DELTA"]
        self.update_intervall = self.config["UPDATE_INTERVALL"]
        self.stop_factor = 1 if self.config["SLOW_STOP"] else 4

    def post(self, data):
        """
        Hier werden die Daten an die Motion durchgereicht, vorher wird auf
        Beschleunigung geachtet. Das passiert in :func:`postz` und nicht in
        :func:`update` damit das walking die aktuellen Daten des Zyklus
        auslesen kann, trotz dem es required wird

        ..warning:: Es wird nur in STATE_PLAYING gelaufen
        """
        data[DATA_KEY_WALKING_RUNNING] = (
            self.ipc.get_motion_state() == STATE_WALKING)
        self.log_counter += 1
        if self.log_counter > 60:
            self.log_counter = 0

        if self.ipc.get_motion_state() != STATE_WALKING:
            self.lastforward = 0
            self.lastsideward = 0
            self.lastangular = 0


        if data[DATA_KEY_GAME_STATUS] != DATA_VALUE_STATE_PLAYING or \
                data[DATA_KEY_WALKING_ACTIVE] is False:
            if self.log_counter is 0:
                debug_m(4, "Walking not active -> Continue")
            if self.lastforward == 0 and self.lastsideward == 0 and self.lastangular == 0:
                # nur wenn wir stehen aus machen
                self.ipc.set_walking_activ(False)
                return
            # sonst stop anfordern
            newforward = 0
            newsideward = 0
            newangular = 0
        else:
            newforward = int(data[DATA_KEY_WALKING_FORWARD])
            newsideward = int(data[DATA_KEY_WALKING_SIDEWARD])
            newangular = int(data[DATA_KEY_WALKING_ANGULAR])
        self.ipc.set_walking_activ(True)

        #this code prevents the robot to run too fast
        #and prevents too abrupt canges of speeds
        #Änderungen nur in definierten Intervallen
        if time.time() - self.updateslower > self.update_intervall:
            forward_delta = newforward - self.lastforward
            forward_stopfactor = self.stop_factor if newforward> 0 and newforward < self.lastforward else 1
            sideward_delta = newsideward - self.lastsideward
            sideward_stopfactor = self.stop_factor if (newsideward> 0 and newsideward < self.lastsideward) or (newsideward < 0 and newsideward > self.lastsideward) else 1
            angular_delta = newangular - self.lastangular
            delta_sum = (abs(forward_delta * self.angularfaktor) + abs(sideward_delta * self.angularfaktor) + abs(angular_delta))/(self.angularfaktor*self.speed_delta)

            self.updateslower = time.time()
            if delta_sum != 0:
                self.lastforward += sign(forward_delta) * min(abs(forward_delta), abs(forward_delta/delta_sum*forward_stopfactor))
                self.lastsideward += sign(sideward_delta) * min(abs(sideward_delta), abs(sideward_delta/delta_sum*sideward_stopfactor))
                self.lastangular += sign(angular_delta) * min(abs(angular_delta), abs(angular_delta * self.angularfaktor/delta_sum))

            self.lastforward = self.maxspeed(self.lastforward, self.max_forward_speed)
            self.lastangular = self.maxspeed(self.lastangular, self.max_angular_speed)
            self.lastsideward = self.maxspeed(self.lastsideward, self.max_sidewards_speed)
            #TODO schneller Stoppen?

        debug_m(4, "RealForward", self.lastforward)
        debug_m(4, "RealSideward", self.lastsideward)
        debug_m(4, "RealAngular", self.lastangular)

        data[DATA_KEY_WALKING_FORWARD_REAL] = self.lastforward
        data[DATA_KEY_WALKING_SIDEWARD_REAL] = self.lastsideward
        data[DATA_KEY_WALKING_ANGULAR_REAL] = self.lastangular

        self.ipc.set_walking_forward(self.lastforward)
        self.ipc.set_walking_sidewards(self.lastsideward)
        self.ipc.set_walking_angular(self.lastangular)

        if self.log_counter is 0:
            debug_m(
                3,
                "Running",
                (self.ipc.get_motion_state() == STATE_WALKING))
            debug_m(3, "XAmplitude", self.lastforward)
            debug_m(3, "YAmplitude", self.lastsideward)
            debug_m(3, "AAmplitude", self.lastangular)

    @staticmethod
    def maxspeed(calc, maxval):
        if calc > 0:
            return min(calc,maxval)
        else:
            return max(calc, -1*maxval)


def register(module_service):
    """Registriert das Modul am Framework"""
    module_service.add(
        MotionWalkingModule,
        "Walking",
        requires=[
            DATA_KEY_IPC,
            DATA_KEY_GAME_STATUS,
            DATA_KEY_CONFIG],
        provides=[DATA_KEY_WALKING,
                  DATA_KEY_MOTION_WALKING,
                  DATA_KEY_MOTION_WALKING,
                  DATA_KEY_WALKING_HIP_PITCH_OUT,
                  DATA_KEY_WALKING_FORWARD,
                  DATA_KEY_WALKING_SIDEWARD,
                  DATA_KEY_WALKING_ANGULAR,
                  DATA_KEY_WALKING_FORWARD_REAL,
                  DATA_KEY_WALKING_SIDEWARD_REAL,
                  DATA_KEY_WALKING_ANGULAR_REAL,
                  DATA_KEY_WALKING_ACTIVE,
                  DATA_KEY_WALKING_RUNNING,
                  DATA_KEY_WALKING_ARMS])
