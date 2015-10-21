# -*- coding: utf8 -*-
"""
BaseMotionServer
^^^^^^^^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* 19.1.14: Aus dem motionserver rausgelöst (Nils Rokita)
* 20.1.14: Walking in Motion Integriert
* 26.1.14: STATE_WALKING eingeführt

Dieses Modul ist die Basis des Motionservers, und kümmert sich um
fallerennung und die verschiedenen Stati der Motion.
Außerdem regelt es die Komunikation mit dem :mod:`ipc`.
"""
from bitbots.ipc.ipc cimport AbstractIPC
from bitbots.robot.pypose cimport PyPose as Pose, PyJoint as Joint
from bitbots.util.pydatavector cimport PyDataVector as DataVector

from bitbots.lowlevel.controller.controller cimport Controller, BulkReadPacket, SyncWritePacket
from bitbots.lowlevel.controller.controller cimport MX28, CM730, ID_CM730
from bitbots.lowlevel.controller.controller import MultiMotorError
from bitbots.lowlevel.simulatorbridge import Simulatorbridge

from bitbots.motion.animation cimport Animation, parse, Animator


#import bitbots.motion.animation as animation
from bitbots.util import find_animation, get_config
#from bitbots.util.datavector import IntDataVector
from bitbots.util.speaker import say
from bitbots.util.nice import Nice
from bitbots.util.config import Config
from bitbots.util.mcanalyse import MotorConnectionAnalyser

from cpython.exc cimport PyErr_CheckSignals

import math
import time
import json
import traceback

from bitbots.debug.debug cimport Scope

include "zmpwalking-impl.pxi"
include "accmovementtracker-impl.pxi"

cdef Scope debug = Scope("Motion.Server")

cdef state_to_string(int state):
    return {
        STATE_CONTROLABLE: "controlable",
        STATE_FALLING: "falling",
        STATE_FALLEN: "fallen",
        STATE_GETTING_UP: "getting up",
        STATE_ANIMATION_RUNNING: "animation running",
        STATE_BUSY: "busy",
        STATE_STARTUP: "startup",
        STATE_PENALTY: "penalty",
        STATE_PENALTY_ANIMANTION: "penalty animation",
        STATE_RECORD: "recording",
        STATE_SOFT_OFF: "soft off",
        STATE_WALKING: "walking",
    }.get(state, "unknown state %d" % state)


cdef class BaseMotionServer(object):
    """
    :class:`BaseMotionServer` wird auf der serverseitigen Seite des
    :ref:`sec_ipc` verwendet, um die vom Client
    angeforderten Bewegungen auf dem Roboter zu übertragen. Außerdem ist es
    seine Aufgabe, die Sensordaten vom Roboter zu lesen und dem Clienten
    bereitzustellen.

    Diese Klasse dient weiterin gewissermaßen als das Kleinhirn des Roboters.
    Selbst wenn die *Denkprozesse* versagen, hilft der :class:`BaseMotionServer`
    dem Roboter dabei, bei einem Sturz nicht herumzuzappeln und eigenständig
    sofort wieder aufzustehen.

    Diese Klasse ist relativ abstrakt gehalten. Die eigentliche Kommunikation
    mit dem Roboter findet in :func:`update_sensor_data` und
    :func:`apply_goal_pose` statt. Eine geerbte Klasse kann dort mit einem
    realen Roboter kommunizieren oder diesen einfach simulieren.
    """

    def __init__(self, ipc, dieflag, standupflag, softoff, softstart):
        self.ipc = ipc
        self.gyro_kalman = TripleKalman()
        self.kinematic_kalman = TripleKalman()
        self.dieflag = dieflag
        self.softoff = softoff
        self.startup_time = time.time()
        self.softstart = softstart
        self.config = get_config()
        self.init_walking()
        self.load_falling_data()
        self.dynamic_animation = self.config["dynamic_animation"]

        # wir wollen ganz viel aufmerksamkeit vom scheduler
        self.nice = Nice(debug)
        self.nice.set_realtime()

        # etwagige penalty flags vergessen, die stören meist
        if self.ipc.get_state() == STATE_PENALTY or self.ipc.get_motion_state() == STATE_PENALTY:
            say("Penalty was set, forget it!", False)
            self.set_state(STATE_STARTUP)
        elif self.ipc.get_state() == STATE_RECORD:
            debug.warning("Recordflag gesetzt, bleibe im record modus")
            debug.warning("Wenn das falsch gesetzt ist, starte einmal das record script und beende es wieder")
            self.set_state(STATE_RECORD)
        else:
            self.set_state(STATE_STARTUP)

        if softstart and not self.state == STATE_RECORD:
            debug << "Softstart"
            # time -120 damit softoff wieder anstellen nicht anspringt
            self.last_client_update = time.time() - 120
            self.last_version = self.ipc.get_version()
            # das muss hgier schon, sonst geht die motion sofort aus,
            # weil er merkt das noch kein update gekommen ist
            self.set_state(STATE_SOFT_OFF)
            self.switch_motor_power(False)
        else:
            self.last_client_update = time.time()
            self.switch_motor_power(True)

        self.goal_pose = Pose()
        self.robo_pose = Pose()
        self.robo_gyro = IntDataVector(0, 0, 0)
        self.robo_accel = IntDataVector(0, 0, 0)
        self.robo_angle = DataVector(0, 0, 0)
        self.smooth_robo_angle_x = 0
        self.long_time_robo_angle_x = 0
        self.kin_robo_angle = DataVector(0, 0, 0)
        self.raw_gyro = IntDataVector(0, 0, 0)

        self.led_head = (0, 0, 255)
        self.led_eye = (0, 0, 255)
        self.button1 = 0
        self.button2 = 0

        self.smooth_accel = DataVector(0, 0, 0)
        self.smooth_gyro = DataVector(0, 0, 0)
        self.not_much_smoothed_gyro = DataVector(0, 0, 0)
        self.standupflag = standupflag
        self.post_anim_state = None

        joints =  self.config['joints']
        debug.log("Set Motor min/max Values")
        with self.ipc:
            for motor in joints:
                if not str(motor['name']) in self.ipc.get_pose_ref().names:
                    debug.warning("Joints.json: unknown motor %s" % str(motor))
                    continue
                if 'max' in motor['limits']:
                    self.ipc.get_pose_ref()[str(motor['name'])].maximum = motor['limits']['max']
                if 'min' in motor['limits']:
                    self.ipc.get_pose_ref()[str(motor['name'])].minimum = motor['limits']['min']

        # wenn das standupflag nicht gesetzt wird, wird auch die anfangs
        # animation nicht gespielt, daher hier auf controlable setzen
        if not self.standupflag and not softstart:
            self.set_state(STATE_CONTROLABLE)

    cpdef load_falling_data(self) :
        self.falling_activated           = self.config["falling"][self.config["RobotTypeName"]]["dynamisches_fallen_aktiviert"]
        self.falling_ground_coefficient  = self.config["falling"][self.config["RobotTypeName"]]["boden_koeffizient"]

        #Fallanimation laden
        self.falling_motor_degrees_front = self.config["falling"][self.config["RobotTypeName"]]["motor_stellungen_vorne"]
        self.falling_motor_degrees_back  = self.config["falling"][self.config["RobotTypeName"]]["motor_stellungen_hinten"]
        self.falling_motor_degrees_right = self.config["falling"][self.config["RobotTypeName"]]["motor_stellungen_rechts"]
        self.falling_motor_degrees_left  = self.config["falling"][self.config["RobotTypeName"]]["motor_stellungen_links"]

        #Fallerkennungs Grenzwerte laden
        self.falling_threshold_front     = self.config["falling"][self.config["RobotTypeName"]]["grenzwert_gyro_y_vorne"] \
                                           * self.falling_ground_coefficient + self.config["ZMPConfig"][self.config["RobotTypeName"]]["HipPitch"]
        self.falling_threshold_back      = self.config["falling"][self.config["RobotTypeName"]]["grenzwert_gyro_y_hinten"]\
                                           * self.falling_ground_coefficient + self.config["ZMPConfig"][self.config["RobotTypeName"]]["HipPitch"]
        self.falling_threshold_right     = self.config["falling"][self.config["RobotTypeName"]]["grenzwert_gyro_x_rechts"]\
                                           * self.falling_ground_coefficient
        self.falling_threshold_left      = self.config["falling"][self.config["RobotTypeName"]]["grenzwert_gyro_x_links"]\
                                           * self.falling_ground_coefficient

        #Grenzwerte an Untergrund anpassen
        self.falling_threshold_front     *= self.falling_ground_coefficient
        self.falling_threshold_back      *= self.falling_ground_coefficient
        self.falling_threshold_right     *= self.falling_ground_coefficient
        self.falling_threshold_left      *= self.falling_ground_coefficient

        return

    cdef ZMPWalkingEngine create_and_parametrize_walking_engine(self):
        cdef ZMPParameter params = ZMPParameter()
        cdef object zmp_config = self.config["ZMPConfig"][self.config["RobotTypeName"]]
        cdef dict zmp_param_config = zmp_config["Parameter"]
        for name in zmp_param_config:
            if hasattr(params, name):
                setattr(params, name, zmp_param_config[name])
            else:
                debug("Konnte ZMPParameter %s nicht setzten. Es scheint ihn nicht zu geben" % name)
        params.pDefault = self.config["mx28config"]["RAM"]["p"]
        walking = ZMPWalkingEngine(params, zmp_config,self.config["RobotTypeName"])

        return walking


    cdef init_walking(self):
        """
        Diese Methode macht das Init des Walkings
        """
        cdef object zmp_config = self.config["ZMPConfig"][self.config["RobotTypeName"]]
        self.walking = self.create_and_parametrize_walking_engine()
        self.walkready_animation = self.walkready_pose(duration=1.5)
        debug("Hip Pitch auf %d gesetzt" % zmp_config["HipPitch"])
        self.with_gyro = zmp_config["use_gyro_for_walking"]
        self.with_tiltX = zmp_config["use_bodyTiltXScaling"]
        self.robo_angle_stop= zmp_config["use_robo_angle_stop"]
        self.smooth_robo_angle_stop_value = zmp_config["robo_angle_stop_value"]
        self.smooth_robo_angle_smoothing= zmp_config["smooth_robo_angle_smoothing"]


        self.walk_active = False
        self.walk_forward = 0
        self.walk_sideward = 0
        self.walk_angular = 0

        # Setze werte im IPC auf 0
        self.ipc.set_walking_activ(False)
        self.ipc.set_walking_forward(0)
        self.ipc.set_walking_sidewards(0)
        self.ipc.set_walking_angular(0)


    cdef Pose calculate_walking(self):
        """
        Setzt die Parameter fürs walking und berechnet die Pose
        """

        # Aktuelle geschwindigkeitswerte Setzen
        self.walking.set_velocity(
            self.walk_forward / 150.0,
            self.walk_sideward / 50.0,
            self.walk_angular / 50.0) # werte aus config erstmal hard TODO
        # Gyro auslesen und an das Walking weitergeben
        cdef int gyro_x, gyro_y, gyro_z
        gyro_x, gyro_y, gyro_z = self.robo_gyro
        if self.with_gyro is True:
            self.walking.set_gyro(gyro_x, gyro_y, gyro_z) ###gyro

        if self.with_tiltX is True and abs(self.smooth_robo_angle_x) > self.smooth_robo_angle_stop_value:
            self.walking.set_tiltX(self.smooth_robo_angle_x, self.long_time_robo_angle_x)
        else:
            self.walking.set_tiltX(0, self.long_time_robo_angle_x)
        # Pose berechnen
        self.zmp_foot_phase = self.walking.process()
        self.ipc.set_walking_foot_phase(self.zmp_foot_phase)
        # Pose zurückgeben
        return self.walking.pose

    cdef void walking_start(self):
        """
        Startet das Walking. Ab sofort wir der Roboter laufen.
        """
        self.walking.start()
        self.walking.stance_reset()

    cdef void walking_reset(self):
        """
        Resettet das Walking und stoppt es dabei *sofort*. Das bedeutet
        das es auch mitten im Schritt in einer instabilen Position anhalten
        kann. Überwiegend zum abbrechen wenn wir gerade Fallen oder
        ähnliches
        """
        self.walking.stop()
        self.walking.stance_reset()
        # TODO

    cdef void walking_stop(self):
        """
        Sagt dem Walking das wir stoppen wollen. Das Walking wird noch
        etwas Weiterlaufen bis es einen Stabilen zustand zum anhalten
        erreicht hat, daher muss weiter :func:`calculate_walking`
        benutzt werden
        """
        self.walking.stop()

    cdef set_state(self, int state):
        """ Updatet den internen Status des MotionServers und publiziert
            ihn zum Clienten
        """
        #Wenn die Motion aus einem State kommt, in dem sie Aufsteht soll der Gyro resettet werden
        if self.state in [
                STATE_FALLEN,
                STATE_FALLING,
                STATE_GETTING_UP,
                STATE_PENALTY,
                STATE_PENALTY_ANIMANTION,
                STATE_STARTUP,
                STATE_BUSY]:
            self.gyro_kalman.reset()

        self.state = state
        # unterdrücke state_soft_off nach außen, das sich clients noch trauen die motion anzusprechen
        # TODO: Etwagige Probleme weil motorpositionen nicht die echten sind überprüfen!!
        self.ipc.set_motion_state(state if state != STATE_SOFT_OFF else STATE_CONTROLABLE)

        debug.log("Setze Status auf '%s'" % state_to_string(state))
        debug.log("Status", state_to_string(state))


    cpdef update_forever(self):
        """ Ruft :func:`update_once` in einer Endlosschleife auf """
        cdef int iteration = 0, errors = 0
        cdef double duration_avg = 0, start = time.time()

        while True:
            self.update_once()

            # Signale prüfen
            PyErr_CheckSignals()

            # im Softoff passiert nichts geschwindigkeit Kritisches, da brauchen
            # wir nicht ständig alles aktuallisieren, entlastet den cpu
            if self.state == STATE_SOFT_OFF:
                time.sleep(0.05)

            # Mitzählen, damit wir eine ungefäre Update-Frequenz bekommen
            iteration += 1
            if iteration < 100:
                continue

            if duration_avg > 0:
                duration_avg = 0.5 * duration_avg + 0.5 * (time.time() - start)
            else:
                duration_avg = (time.time() - start)

            debug.log("Updates/Sec", iteration / duration_avg)
            iteration = 0
            start = time.time()

    cpdef animate(self, name, post_anim_state=None, dict animation=None):
        """ Spielt eine Animation aus einer Datei ab. Dabei werden Befehle
            von einem IPC Client ignoriert, bis die Animation durchgelaufen
            ist.

            Die Animation wird in dieser Methode geladen und als
            :attr:`next_animation` gespeichert, um bei nächster Gelegenheit
            abgespielt zu werden. Wenn die Animation zuende ist, wird der Status
            auf post_anim_status gesetzt, bei NONE auf STATE_CONTROLABLE
        """
        debug.log("Lade Animation '%s'" % name)
        cdef Animation anim
        try:
            if animation is None or not self.dynamic_animation:
                with open(find_animation(name)) as fp:
                    anim = parse(json.load(fp))
            else:
                anim = parse(animation)
        except IOError:
            debug.warning("Animation '%s' nicht gefunden" % name)
            raise

        self.next_animation = anim
        self.post_anim_state = post_anim_state

    cpdef update_once(self):
        """ Updatet die Sensordaten mit :func:`update_sensor_data`,
            ruft die Funktion :func:`evaluate_state` auf und
            wendet neue Daten mit :func:`apply_goal_pose`
            an.

            Außerdem werden die neu gelesenen Daten an den Client weiter
            gegeben. Die Sensordaten der letzten Iterationen werden in
            einem geglätteten Mittelwert als :attr:`smooth_accel` und
            :attr:`smooth_gyro` zur Verfügung gestellt.
        """
        self.update_sensor_data()
        # Daten an den IPC Client senden
        self.ipc.update_positions(self.robo_pose)
        self.ipc.set_gyro(self.robo_gyro) ###gyro
        self.ipc.set_accel(self.robo_accel) ###accel
        self.ipc.set_robot_angle(self.robo_angle) ###angle
        self.ipc.set_button1(self.button1)
        self.ipc.set_button2(self.button2)
        # Gyrowerte geglättet merken
        self.smooth_gyro = self.smooth_gyro * 0.9 + self.raw_gyro * 0.1 ###gyro

        #wird zur Fallerkennung genutzt, smooth_gyro ist dafür zu spät aber peaks muessen trotzdem geglaettet werden
        #glättung erhöhen -->  spätere erkennung
        #glättung verringern --> häufigeres Fehlverhalten, zb.: auslösen des Fallens beim Laufen
        self.not_much_smoothed_gyro = self.not_much_smoothed_gyro * 0.5 + self.raw_gyro * 0.5
        self.smooth_accel = self.smooth_accel * 0.9 + self.robo_accel * 0.1 ###accel

        # Warten, bis Startup erreicht ist.
        if self.startup_time is None or time.time() - self.startup_time > 1:
            if self.startup_time is not None:
                # Wenn wir das erste mal starten, alles initialisieren
                self.startup_time = None
                self.last_version = self.ipc.get_version()
                self.goal_pose.goals = self.robo_pose.positions
                if self.state != STATE_RECORD:
                    #wenn wir in record sind wollen wir da auch bleiben
                    self.ipc.set_state(STATE_CONTROLABLE)

            # wenn der Client neu in Penalized ist, setzen wir uns noch hin
            # sonst wollen wir nichts machen
            if self.ipc.get_state() == STATE_PENALTY:
                # Wenn der Roboter schon penalized ist, hören wir hier auf.
                if self.state == STATE_PENALTY:
                    # Motoren Abstellen, sind nicht nötig, um das interne
                    # handling kümmert sich die implementation (sensor_update
                    # wird weiterhin aufgeruffen)
                    self.switch_motor_power(False)
                    time.sleep(0.05)
                    # wir tuen so als wenn es noch updates vom client gibt
                    # um dafür zu sorgen das es nach dem aufwachen vom
                    # penalty nicht sofort nach softoff oder off aufgrund
                    # der lange zeit (genzwungenen) keine updates geht
                    # (in STATE_PENALTY ist es unmöglich updates and die
                    # notion zu liefern)
                    self.last_client_update = time.time()
                    return
                # sonst hinsetzen, aber nur wenn wir das nicht sowieso schon tun
                if self.state != STATE_PENALTY_ANIMANTION:
                    debug << "Penalized, sit down!"
                    self.animate(
                        self.config["animations"]["motion"]["penalized"], STATE_PENALTY)
                    self.set_state(STATE_PENALTY_ANIMANTION)
                    debug << "Motion wird danach nichts mehr tun, penalized"

            if self.state == STATE_PENALTY:
                # Die Motion ist noch im State Penalty, der Client nicht mehr,
                # wir stehen auf und stehen wieder auf und setzen uns 'steuerbar'.

                # Als erstes stellen wir die Motoren wieder an
                self.switch_motor_power(True)
                # Aktuelle Pose hohlen um Zuckungen zu vermeiden
                self.update_sensor_data()
                self.set_state(STATE_PENALTY_ANIMANTION)
                # Aufstehen
                self.animate(
                    self.config["animations"]["motion"]["walkready"], STATE_CONTROLABLE, self.walkready_animation)

            if self.ipc.get_state() == STATE_RECORD:
                # wenn der Client im Record ist, wollen wir nicht "Controlabel"
                #sein da sonst andere Clienten die Steuerung übernehmen könnten
                if self.state == STATE_SOFT_OFF:
                    #wenn im softoff erstmal aufstehen (Ist besser)
                    self.animate(
                        self.config["animations"]["motion"]["walkready"],
                            STATE_RECORD)
                elif self.state not in (
                        STATE_RECORD,
                        STATE_ANIMATION_RUNNING ,
                        STATE_GETTING_UP,
                        STATE_STARTUP):
                    # wenn wir gerade ne animation spielen gehen wir vermutlich
                    # gerade zum record
                    self.set_state(STATE_RECORD)

            elif self.state == STATE_RECORD:
                # nach abgeschlossener aufnahme wieder in den normalzustand
                # zurückkehren
                self.set_state(STATE_CONTROLABLE)

            # Farbwerte für den Kopf holen
            self.led_eye = self.ipc.get_eye_color().xyz
            self.led_head = self.ipc.get_forehead_color().xyz

            if self.ipc.get_state() != STATE_ANIMATION_RUNNING and self.state != STATE_RECORD:
                # nur evaluieren, wenn der Client keine Animation spielt und
                # nicht im Record Modus ist (den prüfen wir bei uns da wir
                # bevor wir endgültig nach record gehen unter umständen
                # noch eigene dinge tun, danach uns selber m it state
                # record sperren
                self.evaluate_state()

            self.update_goal_pose()
            self.apply_goal_pose()

    cpdef update_sensor_data(self):
        """ Diese Methode sollte in einer Implementierung dieser Klasse
            überschrieben werden und die Daten aus dem Roboter auslesen und
            über die Attribute :attr:`robo_pose`, :attr:`robo_gyro` und
            :attr:`robo_accel` publizieren.

            Diese Methode ist hier nicht implementiert und muss in einer
            geerbten Klasse mit Funktionalität gefüllt werden!
        """
        raise NotImplementedError()

    cpdef apply_goal_pose(self):
        """ Hier soll die neue Zielpose, die über :func:`update_goal_pose`
            berechnet wird, an den Roboter übertragen werden.

            Diese Methode ist hier nicht implementiert und muss in einer
            geerbten Klasse mit Funktionalität gefüllt werden!
        """
        raise NotImplementedError()

    cpdef switch_motor_power(self, state):
        """
        Diese Funktion gibt die möglichkeit bei einer Implementierung mit realen
        Motoren die Motoren an und aus zu stellen.

        :param state: Ob die Motoren an oder aus sein sollen
        :type state: Boolean
        """
        pass

    cpdef evaluate_state(self):
        """ :func:`evaluate_state` ermittelt aus dem zuletzt in
            :func:`update_sensor_data` gespeicherten Zustand die nötigsten
            Aktionen wie *Aufstehen* oder die
            *Gelenke weichstellen*, wenn der Roboter umgefallen ist. Dafür
            ruft sie Funktionen wie :func:`check_queued_animations`
            oder :func:`checked_fallen` auf.
        """
        self.check_queued_animations()
        if self.standupflag:
            self.check_fallen()

    cpdef check_queued_animations(self):
        """ Wenn möglich mit der nächsten Animation beginnen """
        if self.state == STATE_FALLING:
            # Animation abbrechen, wenn wir hinfallen
            self.animfunc = None
            return

        cdef Animator amator
        if self.next_animation is not None and self.robo_pose is not None:
            if self.state == STATE_SOFT_OFF:
                # Wir setzen den timestamp, um dem Softoff mitzuteilen
                # das wir etwas tu wollen.
                self.last_client_update = time.time()
                # warten bis es Aufgewacht ist, dann erst loslegen
                return
            amator = Animator(self.next_animation, self.robo_pose)
            self.animfunc = amator.playfunc(0.025)
            self.next_animation = None

            if self.state == STATE_CONTROLABLE:
                # Ab jetzt spielen wir die Animation
                self.set_state(STATE_ANIMATION_RUNNING)

    cdef info(self, text):
        """ Gibt einen Text plus aktuelle Sensordaten aus. """
        debug << text
        #debug << "gyro  = %s, norm=%1.2f" % (str(self.smooth_gyro), self.smooth_gyro.norm())
        #debug << "accel = %s, norm=%1.2f" % (str(self.smooth_accel), self.smooth_accel.norm())

    cpdef check_fallen(self):
        """ Prüfen, ob der Roboter hingefallen ist oder gerade fällt """
        # beim initialen aufstehen, und beim soft-off nicht prüfen ob er liegt
        # wenn wir gerade eine Animation Spielen (Penalty oder getting up)
        # wollen wir auch nicht aufs fallen auchten
        if self.state not in (
                STATE_GETTING_UP,
                STATE_SOFT_OFF,
                STATE_PENALTY_ANIMANTION):

            #Fallpruefung nach vorne bzw. nach hinten:
            #erstellt von 3doerfle, 3bimberg, 3windsor (Robocup Praktikum 2015)
            #Diskrete Werte stehen in "falling.yaml"
            # Animationen nicht ins Animationsregister übertragen um eventuelles Fehlverhalten (z.B. durch gegenseitiges
            # blockieren verschiedener States) zu vermeiden. und reaktion muss sehr schnell erfolgen.
            #GETESTET FUER: wheatly, Tamara, (Fiona)--> konnte beim test nicht richtig laufen, Goal (nur mit falling_activated = false)
            #Gerade nicht am fallen, (Animation schon aktiv)
            if self.state != STATE_FALLING :
                #falle ich eher zur seite oder nach vorne/hinten?
                if abs(self.not_much_smoothed_gyro.get_y()) > abs(self.not_much_smoothed_gyro.get_x()) :
                    self.check_fallen_forwardAndBackward()
                else:
                    self.check_fallen_sideways()

            #in den nächsten Fallunterscheidungen haben wir den raw_gyro mit reingenommen,
            #da sonst bei aus dem stand umfallen zu frueh auf "ich liege schon" umgeschaltet wurde
            #3doerfle, 3bimberg, 3windsor(Robocup Praktikum 2015)
            if self.state == STATE_FALLING and self.smooth_gyro.norm() < 3 and self.raw_gyro.norm() < 3: ###gyro
                if self.smooth_accel.norm() > 30:
                    self.info("Ich bin hingefallen")
                    self.set_state(STATE_FALLEN)
                else:
                    self.info(
                        "Ich glaube, dass ich doch nicht hingefallen bin")
                    self.set_state(STATE_CONTROLABLE)
                return


            # Nicht so gut, aber funktioniert erstmal
            if self.raw_gyro.norm() < 5 and self.smooth_gyro.norm() < 5 and self.robo_angle.y > 80: ###gyro
                self.info("Ich liege auf dem Bauch, ich sollte aufstehen!")
                self.set_state(STATE_GETTING_UP)
                self.fallState = FALLEN_FRONT_UP
                self.animate(self.config["animations"]["motion"]["front-up"])

            if self.raw_gyro.norm() < 5 and self.smooth_gyro.norm() < 5 and self.robo_angle.y < -60: ###gyro
                self.info("Ich liege auf dem Rücken, ich sollte aufstehen!")
                self.set_state(STATE_GETTING_UP)
                self.fallState = FALLEN_BOTTOM_UP
                self.animate(self.config["animations"]["motion"]["bottom-up"])

            if self.raw_gyro.norm() < 5 and self.smooth_gyro.norm() < 5 and abs(self.robo_angle.x) > 60:
                self.info("Ich liege auf der Seite und sollte aufstehen")
                self.set_state(STATE_GETTING_UP)
                self.fallState = FALLEN_FRONT_UP
                self.animate(self.config["animations"]["motion"]["front-up"])

            if self.state == STATE_FALLEN and self.raw_gyro.norm() < 3 and self.smooth_gyro.norm() < 3:
                self.set_state(STATE_GETTING_UP)
                self.fallState = FALLEN_UPRIGHT
                self.animate(self.config["animations"]["motion"]["walkready"])

        if self.state == STATE_STARTUP:
            self.set_state(STATE_GETTING_UP)
            self.fallState = FALLEN_UPRIGHT
            self.animate(self.config["animations"]["motion"]["walkready"])

    cpdef check_fallen_forwardAndBackward(self):
        # Prüfen ob wir gerade nach HINTEN fallen
        if self.state != STATE_FALLING and self.falling_threshold_back < self.not_much_smoothed_gyro.get_y() : ###HINTEN
            self.info("ICH FALLE NACH HINTEN ")
            self.set_state(STATE_FALLING)
            self.set_falling_pose(self.falling_motor_degrees_back)
            return

         # Prüfen ob wir gerade nach VORNE fallen
        if self.state != STATE_FALLING and self.not_much_smoothed_gyro.get_y() < self.falling_threshold_front: ###VORNE
            self.info("ICH FALLE NACH VORNE")
            self.set_state(STATE_FALLING)
            self.set_falling_pose(self.falling_motor_degrees_front)
            return

        #Funktioniert in den meisten Fällen sehr gut!
    cpdef check_fallen_sideways(self):
        # Prüfen ob wir gerade nach RECHTS fallen
        if self.state != STATE_FALLING and self.not_much_smoothed_gyro.get_x() < self.falling_threshold_right: ###RECHTS
            self.info("ICH FALLE NACH RECHTS")
            self.set_state(STATE_FALLING)
            self.set_falling_pose(self.falling_motor_degrees_right)
            return

        # Prüfen ob wir gerade nach LINKS fallen
        if self.state != STATE_FALLING and self.falling_threshold_left < self.not_much_smoothed_gyro.get_x(): ###LINKS
            self.info("ICH FALLE NACH LINKS")
            self.set_state(STATE_FALLING)
            self.set_falling_pose(self.falling_motor_degrees_left)
            return

    cpdef set_falling_pose(self, object falling_motor_degrees) :
        if self.falling_activated :
            for i in range(1,20) :
                self.goal_pose.get_joint_by_cid(i).goal = falling_motor_degrees[i-1]
        else :
            self.goal_pose.set_active(False)

    cpdef update_goal_pose(self):
        """ Updated :attr:`goal_pose`. Wenn eine Animation läuft, spielt
            die mit hinein. Sonst kommt sie vermutlich vom Client. Außerdem
            werden hier alle anderen Befehle vom Client verarbeitet (walking,
            tracking)
        """
        cdef Pose pose
        cdef Joint joint
        cdef int version

        self.walk_forward = self.ipc.get_walking_forward()
        self.walk_sideward = self.ipc.get_walking_sidewards()
        self.walk_angular = self.ipc.get_walking_angular()
        self.walk_active = self.ipc.get_walking_activ()

        if self.ipc.get_reset_tracking():
            self.ipc.set_last_track(self.ipc.get_last_track())
            self.ipc.set_last_track_time(self.ipc.get_last_track_time())

        if self.animfunc is not None and self.state in (
                STATE_ANIMATION_RUNNING,
                STATE_GETTING_UP,
                STATE_PENALTY_ANIMANTION,
                STATE_BUSY):
            # Wenn gerade eine Animation spielt, nehmen wir die
            # nächste Pose aus der Animation
            pose = self.animfunc(self.robo_pose)
            # wir reseten das walking
            self.walking.set_velocity(0, 0, 0)
            self.walking.stop()
            self.walking.set_active(False)

            if pose is not None:
                self.goal_pose.update(pose)
                return

            # Animation ist zuende
            debug("End of Animation")
            self.animfunc = None
            self.last_version = self.ipc.get_version()
            # TODO: Use config
            if self.state is STATE_GETTING_UP:
                print "FallState: ", self.fallState, "Angle: ", self.robo_angle.y
                if self.fallState is FALLEN_BOTTOM_UP:
                    # Check if bend forward
                    if self.robo_angle.y > self.config["getting-up-angles"]["bendForward"]["min"] \
                            and self.robo_angle.y < self.config["getting-up-angles"]["bendForward"]["max"]:
                        debug.log("Fallen State: FALLEN_BEND_FORWARD")
                        self.fallState = FALLEN_BEND_FORWARD
                        self.animate(self.config["animations"]["motion"]["toSquat"])
                    else:
                        self.set_state(STATE_FALLEN)
                elif self.fallState is FALLEN_FRONT_UP:
                    # Check if bend forward
                    if self.robo_angle.y > self.config["getting-up-angles"]["bendForward"]["min"] \
                            and self.robo_angle.y < self.config["getting-up-angles"]["bendForward"]["max"]:
                        debug.log("Fallen State: FALLEN_BEND_FORWARD")
                        self.fallState = FALLEN_BEND_FORWARD
                        self.animate(self.config["animations"]["motion"]["toSquat"])
                    else:
                        self.set_state(STATE_FALLEN)
                elif self.fallState is FALLEN_BEND_FORWARD:
                    # Check if squatted
                    if self.robo_angle.y > self.config["getting-up-angles"]["squatted"]["min"] \
                            and self.robo_angle.y < self.config["getting-up-angles"]["squatted"]["max"]:
                        debug.log("Fallen State: FALLEN_SQUATTED")
                        self.animate(self.config["animations"]["motion"]["stand-up"])
                        self.fallState = FALLEN_SQUATTED
                    else:
                        self.set_state(STATE_FALLEN)
                elif self.fallState is FALLEN_SQUATTED or self.fallState is FALLEN_UPRIGHT:
                # elif self.fallState is FALLEN_SQUATTED:
                    # if self.robo_angle.y < 30 and self.robo_angle.y > -10: # TODO: Check value
                        # self.animate("walkready")
                        # self.fallState = FALLEN_UPRIGHT
                    # else:
                        # self.state = STATE_FALLEN
                # elif self.fallState is FALLEN_UPRIGHT:
                    if abs(self.robo_angle.y) < 35: # TODO: Check value
                        self.set_state(STATE_CONTROLABLE)
                    else:
                        self.set_state(STATE_FALLEN)
                else:
                    assert False
                if self.state is STATE_FALLEN:
                    self.check_fallen()
                return
            # Status setzen
            if self.post_anim_state is None:
                self.set_state(STATE_CONTROLABLE)
            # Wir kommen vom Standup nach dem Hinfallen und wollen uns vor dem Laufen noch mal stabilisieren
            elif self.post_anim_state == STATE_GETTING_UP:
                self.animate(self.config["animations"]["motion"]["walkready"], animation=self.walkready_animation)
                self.post_anim_state = None
            # spezieller endstatus gewünscht, setzen und wunsch auf null setzen
            else:
                self.set_state(self.post_anim_state)
                self.post_anim_state = None

        if self.walking.running:
            # Das Walking läuft aktuell
            if self.state == STATE_WALKING:
                # Wir Sind im richtigen status, und berechnen die
                # nächste Pose
                if not self.walk_active:
                    # wir laufen, wollen aber anhalten
                    self.walking_stop()
                    # Danach Trotzdem noch weiter die Pose
                    # berechnen, da der Schritt noch beendet werden
                    # sollte
                if self.robo_angle_stop and abs(self.smooth_robo_angle_x) > 5 and (time.time() - self.walking_started) >=0:
                    self.walking_stop()
                self.goal_pose.update(self.calculate_walking())
                self.last_client_update = time.time()
            else:
                # Durch irgendetwas sind wir nichtmehr im STATE_WALKING
                # das bedeutet das wir von der Motion gezwungen wurden
                # etwas anderes zu tun (z.B. Aufstehn/Hinfallen)
                # Dann reseten Wir das Walking und stoppen dabei.
                self.walking_reset()
                p = self.config["mx28config"]["RAM"]["p"]
                i = self.config["mx28config"]["RAM"]["i"]
                d = self.config["mx28config"]["RAM"]["d"]
                for name, joint in self.goal_pose.joints:
                    joint.p = p
                    joint.i = i
                    joint.d = d
        else:  # if self.walking.running:
            # Walking läuft nicht, prüfen opb wir laufen sollen
            if self.walk_active:
                if self.ipc.get_state() in (
                            STATE_CONTROLABLE,
                            STATE_SOFT_OFF,
                            STATE_WALKING
                        ) and self.state in (
                            STATE_CONTROLABLE,
                            STATE_SOFT_OFF,
                            STATE_WALKING
                        ):
                    # Wir machen das Walking an wenn der Client entweder
                    # Controlabel oder in Soft_OFF sind.
                    # STATE_WALKING steht hier mit falls irgendwo etwas
                    # schiefläuft damit wir nicht bei inkonsistenten
                    # zuständen nicht mehr laufen können
                    self.set_state(STATE_WALKING)
                    self.walking_started = time.time()
                    self.walking_start()
            elif self.state == STATE_WALKING:
                # Das Walking ist gestoppt, und wir sollen auch nicht
                # laufen, es ist aber noch STATE_WALKING, dann sind
                # wir gerade erfolgreich angehalten und müssen den Status
                # noch wieder ändern:
                self.set_state(STATE_CONTROLABLE)
                # wir setzen das p value aller motoren neu, da das
                # walking hier rumspielt, es für das meiste andere
                # (auch stehen) nicht gut ist wenn die reduziert sind
                p = self.config["mx28config"]["RAM"]["p"]
                i = self.config["mx28config"]["RAM"]["i"]
                d = self.config["mx28config"]["RAM"]["d"]
                for name, joint in self.goal_pose.joints:
                    joint.p = p
                    joint.i = i
                    joint.d = d

        with self.ipc:
            # Möglicherweise gibt es eine neue Pose vom Client, dann nehmen
            # wir diese, Wenn wir Controlabel sind
            now = time.time()
            version = self.ipc.get_version()
            if version > self.last_version and self.state in (
                    STATE_CONTROLABLE,
                    STATE_WALKING,
                    STATE_RECORD,
                    STATE_SOFT_OFF):
                self.last_client_update = now
                self.last_version = version

                # Pose aus dem IPC holen, interne Kopie updaten und
                # Änderungen im IPC vergessen.
                pose = self.ipc.get_pose_ref()
                self.goal_pose.update(pose)
                pose.reset()

        if self.dieflag and now - self.last_client_update > 60 and \
            not self.state in (
                    STATE_RECORD,
                    STATE_ANIMATION_RUNNING,
                    STATE_WALKING,
                    STATE_PENALTY_ANIMANTION,
                    STATE_PENALTY):
            # es gab in den letzten 60 Sekunden keine Aktuallisierung
            # der Pose vom Client, wir stellen uns hier dann mal aus
            # wenn wir nicht im STATE_RECORD sind, da ist das meistens
            # eher blöd wenn wir einfach ausgehen, wenn wir in
            # STATE_ANIMATION_RUNNING sind, tuen wir selbst offensichtlich
            # etwas, z.B. wieder Aufstehen. Wenn wir im State Walking sind
            # tuen wir auch etwas gerade, beim beenden vom Walking gibt
            # es ein update
            if self.softoff:
                if self.state != STATE_SOFT_OFF:
                    # wir sind schon im Soft-Off
                    debug.log("Gehe in soft-off status")
                    say("Switch to soft-off")
                    if self.state != STATE_CONTROLABLE:
                        # Wenn wir nicht Controllabel sind können wir uns
                        # nicht hinsetzen, macht dann nicht so viel sinn
                        # es zu versuchen.
                        self.set_state(STATE_SOFT_OFF)
                    else:
                        # Wir setzen hier auf Busy da es sonst passieren
                        # könnte das die Animation nicht abgespielt wird
                        self.set_state(STATE_BUSY)
                        self.animate(self.config["animations"]["motion"]["sit-down"], STATE_SOFT_OFF)
            else:
                # wenn wir hierher kommen und softoff sind, dann ist es wohl
                # ein softstart ohne softoff, also ok
                if self.state != STATE_SOFT_OFF:
                    # es soll nur aus gemacht werden
                    debug.warning("Kein Update vom Client in 60 Sekunden")
                    say("No update in the last 60 Seconds")
                    debug.log("Bye")
                    raise SystemExit()
        elif self.state == STATE_SOFT_OFF:
            # Pose resetten um versehentliche sprünge zu vermeiden
            # wir wollen jetzt erstmal aufstehen
            self.goal_pose.reset()
            debug.log("Update nach Softoff eingetroffen reaktivieren")
            self.set_state(STATE_STARTUP)

    cpdef walkready_pose(self, duration=1):
        """
            Erstellt eine neue temporäre ZMPWalkingengine und für eine iteration mit ihr aus
            Danach wird die Pose, die aus der Walkeringiteration folgt
            extrahiert und in eine Animation überführt.
        """
        walking = self.create_and_parametrize_walking_engine()
        # parame walking
        walking.process()
        pose = walking.pose
        #for joint in pose:
        #    joint.set_speed((joint.goal - joint.position)/duration)

        # Eine Animation ist ein dict mit Zusatzinformationen und der
        # Liste der Keyframes. Ein Keyframe ist ein dict mit der "duration"
        # und der Motorzielpositionen "goals"
        animation = {"name": "walkready",
            "keyframes": [{"duration":duration, "goals":{joint[0]:joint[1].goal for joint in pose}}]}

        return animation

cdef run(BaseMotionServer ms):
    """
    Diese Methode führt den Motionserver in einer Loop aus, und kümmert
    sich um das runterfahren
    """
    try:
        ms.update_forever()
    except KeyboardInterrupt:
        pass
    except BaseException as e:
        debug.error(e, "Error in Motion: ")
        raise
    finally:
        if ms.state == STATE_SOFT_OFF:
            # Die motoren sind aus, beim hinsetzen würden nur
            # rumhüpfen passieren
            # daher müssen wir nichts weiter tun...
            say("Switch of Motion", True)
            return
        ms.set_state(STATE_BUSY)
        if ms.standupflag:
            # wenn er sich nicht bewegen soll, ist meist das hinsetzen
            # auch unerwünscht
            ms.animate(ms.config["animations"]["motion"]["sit-down"])
            start = time.time()
            while time.time() - start < 1:
                try:
                    ms.update_once()
                except:
                    pass
        else:
            say("Switch of Motors Now!", True) # Blocking Call
            time.sleep(2) # ein klein wenig Zeit geben

