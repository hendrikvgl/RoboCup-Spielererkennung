#-*- coding:utf-8 -*-
"""
ZMPWalkingModule
^^^^^^^^^^^^^^^^

Das WalkingModule kümmert sich um die Ansteuerung und Parametresierung
der Walkingengine. Dabei sorgt sie dafür das es nach möglichkeit nicht
zu zu heftigen Änderungen und Werten kommt

History:
''''''''

* 28.08.13: Erstellt (Robert Schmidt)

* 06.08.14 Refactor (Marc Bestmann)

"""

import time

from bitbots.modules.abstract import AbstractProcessModule
from bitbots.modules.abstract.abstract_module import debug_m
from bitbots.modules.keys import DATA_VALUE_STATE_PLAYING, DATA_KEY_GAME_STATUS, DATA_KEY_CONFIG, DATA_KEY_IPC, \
    DATA_KEY_WALKING_ARMS, DATA_KEY_WALKING_ANGULAR, DATA_KEY_WALKING_FORWARD, DATA_KEY_WALKING_SIDEWARD, \
    DATA_KEY_WALKING_ACTIVE, DATA_KEY_ZMP_WALKING, DATA_KEY_WALKING_SIDEWARD_REAL, DATA_KEY_WALKING_FORWARD_REAL, \
    DATA_KEY_WALKING_ANGULAR_REAL, DATA_KEY_WALKING_RUNNING, DATA_KEY_WALKING, DATA_KEY_WALKING_HIP_PITCH_OUT
from bitbots.util.nice import Nice
from bitbots.util import get_config

config = get_config()


class ZMPWalkingModule(AbstractProcessModule):
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

    def __init__(self):
        super(ZMPWalkingModule, self).__init__(
            requires=[DATA_KEY_IPC, DATA_KEY_CONFIG, DATA_KEY_GAME_STATUS,
                      DATA_KEY_WALKING_FORWARD, DATA_KEY_WALKING_SIDEWARD,
                      DATA_KEY_WALKING_ANGULAR, DATA_KEY_WALKING_ACTIVE, DATA_KEY_WALKING_ARMS],
            provides=[
                DATA_KEY_WALKING_FORWARD_REAL, DATA_KEY_WALKING_SIDEWARD_REAL,
                DATA_KEY_WALKING_ANGULAR_REAL, DATA_KEY_WALKING_ARMS,
                DATA_KEY_WALKING_RUNNING, DATA_KEY_ZMP_WALKING])

        self.USE_GYRO = config["USE_GYRO"]

        zmpconfig = config["ZMPConfig"][config["RobotTypeName"]]
        self.forward_factor = zmpconfig["FORWARD_FACTOR"]
        self.angle_factor = zmpconfig["ANGLE_FACTOR"]
        self.sideward_factor = zmpconfig["SIDEWARD_FACTOR"]
        self.sleeptime = 0.005

    def start(self, data):
        """
        Ließt einige werte aus der Config, und setzt die Startparameter
        """
        #arme am anfang richtig setzen, bevor multithreading das kaputt
        #macht
        config = data[DATA_KEY_CONFIG]
        self.set_init(
            DATA_KEY_WALKING_HIP_PITCH_OUT,
            config["ZMPConfig"][config["RobotTypeName"]]["HipPitch"], data)
        self.set_init(DATA_KEY_WALKING_FORWARD, 0, data)
        self.set_init(DATA_KEY_WALKING_SIDEWARD, 0, data)
        self.set_init(DATA_KEY_WALKING_ANGULAR, 0, data)
        self.set_init(DATA_KEY_WALKING_FORWARD_REAL, 0, data)
        self.set_init(DATA_KEY_WALKING_SIDEWARD_REAL, 0, data)
        self.set_init(DATA_KEY_WALKING_ANGULAR_REAL, 0, data)
        self.set_init(DATA_KEY_WALKING_ACTIVE, False, data)
        self.set_init(DATA_KEY_WALKING_RUNNING, False, data)
        self.set_init(DATA_KEY_WALKING_ARMS, True)
        self.set_init(DATA_KEY_WALKING_ARMS,
                      not data[DATA_KEY_CONFIG]["walking.armsOff"])

        self.nice = Nice(self.debug)

    def update(self, data):
        """
        Hier wird mit absicht nichts getan, Warum das so ist wird
        in :func:`post` erklärt
        """
        # Tut beabsichtigt nichts, siehe self.post()
        pass

    def post(self, data):
        """
        Hier wird das Synkronisieren mit dem Data dict gemacht was
        normalerweise in :func:`update` passiert. Das ist so gelöst
        um probleme beim require und provide zu umgehen, da andere
        Module das Walking requiren, genaugenommen die Werte dafür
        aber Providen. Damit Trotz das die Walking in der abhängigkeits
        Kette vorne steht die werde erst am ende ausgelesen werden
        wird das hier gemacht
        """
        super(ZMPWalkingModule, self).update(data)

    def run(self):
        #Später import, da das ZMPWalking nich mehr gebaut wird, sondern ein Teil der Motion ist @Robert 04.08.2014
        from bitbots.motion.zmpwalking import ZMPWalkingEngine

        ipc = self.get(DATA_KEY_IPC)
        config = self.get(DATA_KEY_CONFIG)
        zmp_config = config["ZMPConfig"]
        ipc_was_controllable = False
        self.walking = ZMPWalkingEngine()
        self.walking.r_shoulder_roll_offset = zmp_config["r_shoulder_roll"]
        self.walking.l_shoulder_roll_offset = zmp_config["l_shoulder_roll"]
        self.walking.hip_pitch_offset = zmp_config["hip_pitch"]
        self.walking.hip_pitch = zmp_config["HipPitch"]
        max_speed = zmp_config["MAX_SPEED"]
        update_intervall = zmp_config["UPDATE_INTERVALL"]
        speed_delta = zmp_config["SPEED_DELTA"]
        debug_m(
            2,
            "Hip Pitch auf %d gesetzt" % config["ZMPConfig"]["HipPitch"])

        # wir wollen maximal mögliche aufmerksamkeit von scheduler
        self.nice.set_realtime()

        log_counter = -1
        last_time = time.time()
        velocity = (0, 0, 0)
        lastforward = 0
        lastsideward = 0
        lastangular = 0
        forward = 0
        sideward = 0
        angular = 0
        updateslower = time.time()
        stop_request = 0
        while True:
            log_counter += 1
            if log_counter > 60:
                log_counter = 0
            if not ipc.controlable or \
                            self.get(DATA_KEY_GAME_STATUS) != DATA_VALUE_STATE_PLAYING:
                time.sleep(0.5)
                if not ipc.controlable:
                    debug_m(4, "IPC not Controllable -> continue")
                    ipc_was_controllable = False
                    continue
                debug_m(4, "Game State not STATE_PLAYING -> continue")
                self.stop_walking()
                continue
            if self.get("Walking.Active") is False:
                self.stop_walking()
                if self.walking.running is False:
                    if log_counter is 0:
                        debug_m(4, "Walking not active -> Continue")
                    time.sleep(self.sleeptime)
                    # Damit bei Walking.active=false nicht getrippelt wird
                    continue
            #this code prevents the robot to run too fast
            #and prevents too abrupt canges of speeds
            if time.time() - updateslower > update_intervall:
                newforward = int(self.get("Walking.Forward"))
                if newforward == lastforward:
                    forward = newforward
                elif lastforward < newforward:
                    if lastforward < 0:
                        forward = min(
                            lastforward + speed_delta,
                            newforward)
                    else:  # newforward >= 0
                        forward = min(
                            lastforward + speed_delta,
                            newforward,
                            max_speed)
                else:  # lastforward >= newforward:
                    if lastforward < 0:
                        forward = max(
                            lastforward - speed_delta,
                            newforward,
                            -max_speed)
                    else:  # lastforward >= 0
                        forward = max(
                            lastforward - speed_delta,
                            newforward)

                newsideward = int(self.get("Walking.Sideward"))
                if newsideward == lastsideward:
                    sideward = newsideward
                elif lastsideward < newsideward:
                    if lastsideward < 0:
                        sideward = min(
                            lastsideward + speed_delta,
                            newsideward)
                    else:  # newforward >= 0
                        sideward = min(
                            lastsideward + speed_delta,
                            newsideward,
                            max_speed)
                else:  # lastforward >= newforward:
                    if lastsideward < 0:
                        sideward = max(
                            lastsideward - speed_delta,
                            newsideward,
                            -max_speed)
                    else:  # lastforward >= 0
                        sideward = max(
                            lastsideward - speed_delta,
                            newsideward)

                newangular = int(self.get("Walking.Angular"))
                if newangular == lastangular:
                    angular = newangular
                elif lastangular < newangular:
                    if lastangular < 0:
                        angular = min(lastangular + speed_delta, newangular)
                    else:  # newforward >= 0
                        angular = min(
                            lastangular + speed_delta,
                            newangular,
                            max_speed)
                else:  # lastforward >= newforward:
                    if lastangular < 0:
                        angular = max(
                            lastangular - speed_delta,
                            newangular,
                            -max_speed)
                    else:  # lastforward >= 0
                        angular = max(
                            lastangular - speed_delta,
                            newangular)
                updateslower = time.time()
            lastforward = forward
            lastsideward = sideward
            lastangular = angular
            if not (velocity == (forward, sideward, angular)):
                debug_m(2, "Set new velocity (%.2d %.2d %.2d)" % (forward,
                                                                  sideward,
                                                                  angular))
                velocity = (forward, sideward, angular)
                if self.walking.running is False:
                    self.reset_walking()
                self.walking.velocity = (forward / self.forward_factor,
                                         sideward / self.sideward_factor,
                                         angular / self.angle_factor)

            x_move_amplitude, y_move_amplitude, a_move_amplitude = self.walking.velocity
            self.set(
                "Walking.Forward.Real",
                x_move_amplitude * self.forward_factor)
            self.set(
                "Walking.Sideward.Real",
                y_move_amplitude * self.sideward_factor)
            self.set(
                "Walking.Angular.Real",
                a_move_amplitude * self.angle_factor)

            if log_counter is 0:
                debug_m(3, "Running", self.walking.running)
                debug_m(3, "XAmplitude", x_move_amplitude)
                debug_m(3, "YAmplitude", y_move_amplitude)
                debug_m(3, "AAmplitude", a_move_amplitude)

            gyro = ipc.get_gyro()
            gyro_x = gyro.x
            gyro_y = gyro.y
            gyro_z = gyro.z
            self.walking.gyro = (gyro_x, gyro_y, gyro_z)

            with Timer("Walking", self.debug):
                # Etwas bewegen
                if ipc_was_controllable is False or \
                                self.walking.running is False:
                    self.reset_walking()
                self.walking.process()

            if self.walking.running:
                self.set("Walking.Running", True)

                pose = self.walking.pose
                # Pose updaten
                with Timer("Update IPC Pose", self.debug):
                    ipc.update(pose)
                    pose.reset()
            else:
                stop_request = stop_request + 1
                if stop_request is 100:
                    self.set("Walking.Running", False)
                    stop_request = 0

            # Etwas warten und geht weiter!
            t = time.time()
            dt = t - last_time
            last_time = t
            time.sleep(max(0, self.sleeptime - dt))
            ipc_was_controllable = ipc.controlable

    def stop_walking(self):
        self.set("Walking.Forward", 0)
        self.set("Walking.Sideward", 0)
        self.set("Walking.Angular", 0)
        self.set("Walking.Forward.Real", 0)
        self.set("Walking.Sideward.Real", 0)
        self.set("Walking.Angular.Real", 0)
        self.set("Walking.Running", False)
        velocity = (0, 0, 0)
        self.walking.velocity = velocity
        self.walking.stop()

    def reset_walking(self):
        self.walking.start()
        self.walking.stance_reset()


class Timer(object):
    __slots__ = ("name", "start", "debug")

    def __init__(self, name, debug):
        self.name = name
        self.start = None
        self.debug = debug

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *ignore):
        duration = 1000 * (time.time() - self.start)
        debug_m(2, self.name, "brauchte %1.2fms" % duration)


def register(ms):
    ms.add(ZMPWalkingModule, "Walking",
           requires=[DATA_KEY_IPC,
                     DATA_KEY_GAME_STATUS,
                     DATA_KEY_CONFIG],
           provides=[DATA_KEY_WALKING,
                     DATA_KEY_ZMP_WALKING,
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
