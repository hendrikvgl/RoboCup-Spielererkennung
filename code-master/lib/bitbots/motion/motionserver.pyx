# -*- coding: utf8 -*-
"""
MotionServer
^^^^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>

History:

* 19.1.14: Vom rest ders Motionservers Getrennt (Nils Rokita)

Dieses Modul fürt die befehle der Motion auf der HArdware über einen
Serielen Bus aus. Der Serielle Buss kan dabei Simuliert sein
"""
from cython.operator cimport dereference as deref
from libcpp cimport bool
from bitbots.ipc.ipc cimport AbstractIPC
from bitbots.ipc import SharedMemoryIPC
from bitbots.lowlevel.serial cimport Serial
from bitbots.robot.pypose cimport PyPose as Pose, PyJoint as Joint
from bitbots.util.pydatavector cimport PyDataVector as DataVector
from bitbots.util.pydatavector cimport PyIntDataVector as IntDataVector
#from bitbots.util.pydatavector cimport IntDataVector as CIntDataVector
from bitbots.util.pydatavector cimport DataVector as CDataVector
from bitbots.util.pydatavector cimport wrap_int_data_vector, wrap_data_vector

from bitbots.lowlevel.controller.controller cimport Controller, BulkReadPacket, SyncWritePacket
from bitbots.lowlevel.controller.controller cimport MX28, CM730, ID_CM730
from bitbots.lowlevel.controller.controller import MultiMotorError, MotorError
from bitbots.lowlevel.simulatorbridge import Simulatorbridge

from bitbots.util import get_config, Joints as JointManager
from bitbots.util.speaker import say
from bitbots.util.nice import Nice
from bitbots.util.config import get_special_config
from bitbots.util.mcanalyse import MotorConnectionAnalyser

from bitbots.util.kalman cimport TripleKalman
from bitbots.util.kinematicutil cimport kinematic_robot_angle

from bitbots.motion.motionserver cimport BaseMotionServer, run
from bitbots.motion.motionserver cimport STATE_PENALTY, STATE_SOFT_OFF, STATE_WALKING, STATE_GETTING_UP

from cpython.exc cimport PyErr_CheckSignals

import math
import time
import json
import traceback

from bitbots.debug.debug cimport Scope
cdef Scope debug = Scope("Motion.Server")


cdef class MotionServer(BaseMotionServer):
    """
    Implementation von :class:`BaseMotionServer` um mit einem echten
    Roboter über :class:`~controller.Controller` *ctrl* zu kommunizieren.
    """
    def __init__(self, ipc, ctrl, dieflag, standupflag, softoff, softstart, bool cm_370=True):

        # diese drei Variablen _müssen_ initialisiert sein, bevor super
        # aufgerufen wird, da der Konstruktor vom  :class:`BaseMotionServer`
        # die Funktion :func:`switch_motor_status` aufruft welche von dieser
        # Klasse überschrieben wird, wenn diese Variablen dann nicht
        # initialisiert sind, kommt es zu einem Segfault
        self.is_soft_off = False
        self.cm_370 = cm_370
        self.ctrl = ctrl
        config = get_config()
        self.motors = config[config["RobotTypeName"]]["motors"]
        if self.cm_370:
            self.dxl_power = self.ctrl.read_register(ID_CM730, CM730.dxl_power)
        else:
            self.dxl_power = True
        motorconf = get_config()["mx28config"]
        self.motor_ram_config = motorconf["RAM"]

        super(MotionServer, self).__init__(ipc, dieflag, standupflag, softoff, softstart)

        self.last_io_success = -1
        self.data_send_last = 0
        self.init_read_packet()
        self.last_overload = {}
        self.overload_count = {}
        offsets = get_special_config("offset")
        self.joint_offsets =  {}
        joint_manager = JointManager()
        for i in range(1,31): #TODO: haende foo
            self.joint_offsets[i] = offsets[joint_manager.get_motor_name(i)]
        self.last_gyro_update_time = time.time()
        self.robot = Robot()
        self.last_kinematic_robot_angle = (0,0)

    cdef set_motor_ram(self):
        """
        Diese Methode setzt die Werte im Ram der Motoren, je nach wert aus
        der Configdatei
        """
        if self.config['setMXRam']:
            debug << "setze MX28 RAM"
            if self.cm_370:
                self.ctrl.write_register(ID_CM730, CM730.led_head, (255, 0, 0))
            for motor in self.motors:
                for conf in self.motor_ram_config:
                    self.ctrl.write_register(motor, MX28.get_register_by_name(conf),
                        self.motor_ram_config[conf])
            if self.cm_370:
                self.ctrl.write_register(ID_CM730, CM730.led_head, (0, 0, 0))
            debug << "Setze Ram Fertig"


    cdef init_read_packet(self):
        """
        Initiallisiert die :class:`BulkReadPacket` für die Kommunikation mit
        den Motoren
        """
        self.read_packet = BulkReadPacket()
        self.read_packet2 = BulkReadPacket()
        self.read_packet3 = BulkReadPacket()
        for name, joint in Pose().joints:
            if joint.cid in self.motors:
                # if robot has this motor
                self.read_packet.add(
                    joint.cid,
                    (
                        MX28.present_position,
                        MX28.present_speed,
                        MX28.present_load,
                        MX28.present_voltage,
                        MX28.present_temperature
                    ))
                self.read_packet3.add(
                    joint.cid,
                    (
                        MX28.present_position,
                    ))
        if self.cm_370:
            self.read_packet.add(
                ID_CM730,
                (
                    CM730.button,
                    CM730.padding31_37,
                    CM730.gyro,
                    CM730.accel,
                    CM730.voltage
                ))
            self.read_packet2.add(
                ID_CM730,
                (
                    CM730.button,
                    CM730.padding31_37,
                    CM730.gyro,
                    CM730.accel,
                    CM730.voltage
                ))
            self.read_packet3.add(
                ID_CM730,
                (
                    CM730.gyro,
                    CM730.accel
                ))

    cpdef update_sensor_data(self):
        cdef dict result
        cdef int say_error
        # Das all_data Flag wird dazu benutzt das dann mehr daten
        # (tmperatur etc) abgefragt werden. Außerdem werden dann daten
        # an das Debug gesendet
        cdef int all_data = False
        if self.data_send_last > 40:
            all_data = True
        try:
            if self.dxl_power:
                if all_data:
                    result = self.ctrl.process(self.read_packet)
                else:
                    result = self.ctrl.process(self.read_packet3)
            else:
                result = self.ctrl.process(self.read_packet2)
        except IOError, e:
            debug << "Lesefehler: " + str(e)
            if self.last_io_success > 0 and time.time() - self.last_io_success > 2:
                debug.warning("Motion hängt!")
                raise SystemExit("Motion hängt!")
            elif not  self.last_io_success > 0:
                self.last_io_success = time.time() + 5
                # Das sieht komisch aus, ist aber absicht:
                # Wenn er nimals daten bekommt soll er _irgentwann_ auch
                # aufhören es zu versuchen
            return

        except MultiMotorError as errors:
            is_ok = True
            for e in errors:
                say_error = True
                err = e.get_error()
                if (err >> 0 & 1) == 1: # Imput Voltage Error
                    pass # die sind meist sowieso mist
                if (err >> 1 & 1) == 1: # Angel Limit Error
                    is_ok = False
                if (err >> 2 & 1) == 1: # Overheating Error
                    is_ok = False
                if (err >> 3 & 1) == 1: # Range Error
                    is_ok = False
                if (err >> 4 & 1) == 1: # Checksum Error
                    is_ok = False
                if (err >> 5 & 1) == 1: # Overload Error
                    say_error = False
                    if e.get_motor() in self.last_overload and \
                      time.time() - 2 < self.last_overload[e.get_motor()]:
                        self.overload_count[e.get_motor()] += 1
                        if self.overload_count[e.get_motor()] > 60:
                            debug.warning("Raise long holding overload error")
                            is_ok = False # dann wirds jetzt weitergegen
                    else:
                        # resetten, der letzte ist schon ne weile her
                        self.overload_count[e.get_motor()] = 0
                        debug.warning("Motor %d hat einen Overloaderror, "
                            % e.get_motor() + " ignoring 60 updates")
                    self.last_overload[e.get_motor()] = time.time()
                if (err >> 6 & 1) == 1: # Instruction Error
                    is_ok = False
                if (err >> 7 & 1) == 1: # Unused
                    is_ok = False
                if say_error:
                    debug.error(err, "A Motor has had an error:")
            if not is_ok:
                # wenn es nicht alles behandelt wurde wollen wir es
                # weiterreichen (führt zum beenden der Motion)
                raise
            # wenn der fehler ignoriert wurde müssen wir prüfen ob ein packet
            # angekommen ist, wenn nicht abbrechen da
            # sonst ein unvollständiges packet verarbeitet wird
            result = errors.get_packets()
            if not result:
                return


        self.last_io_success = time.time()

        cdef Pose pose = self.robo_pose

        cdef Joint joint
        cdef IntDataVector accel = None
        cdef IntDataVector gyro = None
        #cdef maxtmp = 0, maxcid = -1
        #cdef min_voltage = 1e10, max_voltage = 0
        cdef position = None, speed=None, load=None
        cdef voltage = None, temperature=None, button=None

        for cid, values in result.iteritems():
            if cid == ID_CM730:
                if not all_data and self.dxl_power:
                    gyro, accel = values
                else:
                    button, _, gyro, accel, voltage = values
                    debug.log("CM730.Voltage", voltage)
                    if voltage < 105:
                        debug.warning("Low Voltage!!")
                    if voltage < 100:
                        say("Warning: Low Voltage! System Exit!")
                        debug.warning("SYSTEM EXIT: LOW VOLTAGE")
                        raise SystemExit("SYSTEM EXIT: LOW VOLTAGE")
            else:
                joint = pose.get_joint_by_cid(cid)
                if not all_data:
                    position = values[0]
                else:
                    position, speed, load, voltage, temperature = values
                    joint.set_load(load)

                position = position - self.joint_offsets[cid]
                joint.set_position(position)


                # Debug Informationen senden (nur alle 40, wegen der Datenmenge)

                if all_data:  # etwa alle halbe sekunde
                    debug.log("MX28.%d.Temperatur" % cid, temperature)
                    debug.log("MX28.%d.Voltage" % cid, voltage)
                    debug.log("MX28.%d.Load" % cid, load)

                if temperature > 60:
                    fmt = "Motor cid=%d hat eine Temperatur von %1.1f°C: Notabschaltung!"
                    debug.warning(fmt % (cid, temperature))
                    say("An Motor has a Temperatur over %.1f°C" % temperature)
                    raise SystemExit(fmt % (cid, temperature))

                #if temperature > maxtmp:
                #    # Maximale Temperatur merken.
                #    maxtmp = temperature
                #    maxcid = cid

                #max_voltage = max(max_voltage, voltage)
                #min_voltage = min(min_voltage, voltage)

        if all_data:  # etwa alle halbe sekunde
            #debug.log("Temperatur.Max", maxtmp)
            #debug.log("Temperatur.Max.Cid", maxcid)
            #debug.log("Voltage.Max", max_voltage)
            #debug.log("Voltage.Min", min_voltage)
            self.data_send_last = 0
        self.data_send_last += 1

        # TODO: Hartcoded stuff
        #joint = pose.get_joint_by_cid(28)
        #pose.get_joint_by_cid(30).position = joint.position
        #pose.get_joint_by_cid(30).load = joint.load

        cdef double dt, t
        cdef CDataVector angles
        #cdef Vector3f accle
        if gyro is not None and accel is not None:
            t = time.time()
            dt = t - self.last_gyro_update_time
            self.last_gyro_update_time = t

            # Das ist veraltet (zumindest momentan @Nils 30.3.15
            #if self.config["RobotTypeName"] == "Hambot":
            #    # Goal hat den Gyro verdreht eingebaut
            #    accel = IntDataVector(accel.y, 1024 - accel.z, 1024 - accel.x)
            #    gyro = IntDataVector(gyro.z, gyro.x, gyro.y)

            self.robo_accel = accel - IntDataVector(512, 512, 512)
            #print "Accel ungedreht %s" % self.robo_accel
            #self.robo_accel = verdrehe_bla(self.robo_accel)
            #print "Accel gedreht %s" % self.robo_accel
            self.raw_gyro = gyro - IntDataVector(512, 512, 512)

            angles = calculate_robot_angles(deref(self.robo_accel.get_data_vector()))
            #TODO Das verdrehe bla ist teil eines Features um Hambot momentan verdrehen Gyro zu fixen
            #angles = self.gyro_kalman.get_angles_pvv(angles, verdrehe_bla(gyro - IntDataVector(512, 512, 512)), dt)
            angles = self.gyro_kalman.get_angles_pvv(angles, gyro - IntDataVector(512, 512, 512), dt)
            self.robo_angle = wrap_data_vector(angles)
            self.smooth_robo_angle_x = self.smooth_robo_angle_x*(1- self.smooth_robo_angle_smoothing) + self.smooth_robo_angle_smoothing * self.robo_angle.x
            if dt > 1:
                self.long_time_robo_angle_x = self.long_time_robo_angle_x*(1 - self.smooth_robo_angle_smoothing) + self.smooth_robo_angle_smoothing * self.smooth_robo_angle_x
            self.robo_gyro = self.raw_gyro #self.gyro_kalman.get_rates_v()

            self.robot.update(self.robo_pose)
            new_angle = kinematic_robot_angle(self.robot, self.zmp_foot_phase)
            diff = (new_angle[0] - self.last_kinematic_robot_angle[0]) / dt, (new_angle[1] - self.last_kinematic_robot_angle[1]) / dt
            angles.set_x(new_angle[0])
            angles.set_y(new_angle[1])
            angles = self.kinematic_kalman.get_angles_vfv(angles, CDataVector(diff[0],diff[1], 0.0), dt)
            self.last_kinematic_robot_angle = new_angle
            self.kin_robo_angle = wrap_data_vector(angles)


            #print "robo accel %s, kinematic_angle %s, robAngle %s" % (self.robo_accel, self.kin_robo_angle, self.robo_angle)
            diff_angles = (self.robo_angle - self.kin_robo_angle)

        if button is not None:
            self.button1 = button & 1
            self.button2 = (button & 2) >> 1

    cpdef apply_goal_pose(self):
        cdef Pose pose = self.goal_pose
        cdef SyncWritePacket packet
        
        if pose is None:
            return

        # Hier werden die Augenfarben gesetzt.
        # Dabei kann in der Config angegeben werden ob die Augen bei Penalty
        # rot werden, und ob sie ansonsten überhaupt genutzt werden
        if self.cm_370:
            packet = SyncWritePacket((CM730.led_head, CM730.led_eye))
            if self.state == STATE_PENALTY and self.config["EyesPenalty"]:
                packet.add(ID_CM730, ((255, 0, 0), (0, 0, 0)))
            else:
                if self.config["EyesOff"]:
                    packet.add(ID_CM730, ((0, 0, 0), (0, 0, 0)))
                else:
                    packet.add(ID_CM730, (self.led_head, self.led_eye))

            self.ctrl.process(packet)

        cdef Joint joint
        cdef Joint joint2
        cdef SyncWritePacket goal_packet = None
        cdef SyncWritePacket torque_packet = None
        cdef SyncWritePacket p_packet = None
        cdef SyncWritePacket i_packet = None
        cdef SyncWritePacket d_packet = None
        cdef int joint_value = 0

        if self.state != STATE_SOFT_OFF:

            if self.is_soft_off:
                self.is_soft_off = False
                self.switch_motor_power(True)
                # Aktuallisieren der Pose, da die Motoren mit hoher
                # warscheinlichkeit anders liegen als beim ausstellen
                self.update_sensor_data()
                # hier abbrechen um Zuckungen zu vermeiden
                return

            # TODO: Hardcoded Stuff (ganz doof)
            # momentan veraltet 30.3.15 @Nils
            #joint = pose.get_joint_by_cid(30)
            #joint2 = pose.get_joint_by_cid(27)
            #joint2.p = joint.p
            #joint2.goal = joint.goal * -1
            #joint2.speed = joint.speed
            #joint2.active = joint.active
            #joint2 = pose.get_joint_by_cid(28)
            #joint2.p = joint.p
            #joint2.goal = joint.goal
            #joint2.speed = joint.speed
            #joint2.active = joint.active
            #joint.reset()

            goal_packet = SyncWritePacket((MX28.goal_position, MX28.moving_speed))
            for name, joint in pose.joints:
                if not joint.has_changed():
                    continue

                # changed-Property wieder auf false setzen.
                joint.reset()

                if joint.is_active():
                    joint_value = int(joint.get_goal()) + \
                        self.joint_offsets[joint.get_cid()]
                    goal_packet.add(joint.get_cid(),
                        (joint_value, joint.get_speed()))
                else:  # if joint.get_cid() != 30:
                    # Torque muss nur aus gemacht werden, beim setzen eines
                    # Goals geht es automatisch wieder auf 1
                    # Das Torque-Packet nur erstellen, wenn wir es benötigen
                    # 30 ist virtuell und braucht daher nicht gesetzt werden
                    if torque_packet is None:
                        torque_packet = SyncWritePacket((MX28.torque_enable,))

                    # Motor abschalten
                    torque_packet.add(joint.get_cid(), (0, ))

                if joint.get_p() != -1:
                    if p_packet is None:
                        p_packet = SyncWritePacket((MX28.p,))
                    p_packet.add(joint.get_cid(), (joint.get_p(), ))
                    #print "set p:", joint.get_p(), joint.get_cid()

                if joint.get_i() != -1:
                    if i_packet is None:
                        i_packet = SyncWritePacket((MX28.i,))
                    i_packet.add(joint.get_cid(), (joint.get_i(), ))
                    #print "set p:", joint.get_p(), joint.get_cid()

                if joint.get_d() != -1:
                    if d_packet is None:
                        d_packet = SyncWritePacket((MX28.d,))
                    d_packet.add(joint.get_cid(), (joint.get_d(), ))
                    #print "set p:", joint.get_p(), joint.get_cid()

            # Zielwerte setzen
            self.ctrl.process(goal_packet)
            if torque_packet is not None:
                # Motoren abschalten, wennn nötig.
                self.ctrl.process(torque_packet)
            if p_packet is not None:
                self.ctrl.process(p_packet)
            if i_packet is not None:
                self.ctrl.process(i_packet)
            if d_packet is not None:
                self.ctrl.process(d_packet)
        else:
            if not self.is_soft_off:
                self.switch_motor_power(False)
                self.is_soft_off = True

    cpdef switch_motor_power(self, state):
        # wir machen nur etwas be änderungen des aktuellen statusses
        if not self.cm_370:
            # without the cm370 we cant switch the motor power # TODO muss hier noch was gemacht werden????
            return
        if state and not self.dxl_power:
            # anschalten
            debug << "Switch dxl_power back on"
            self.ctrl.write_register(ID_CM730, CM730.dxl_power, 1)
            # wir warten einen Augenblick bis die Motoeren auch wirklich wieder
            # wieder an und gebootet sind
            time.sleep(0.3)
            self.set_motor_ram()
            self.dxl_power = True
        elif (not state) and self.dxl_power:
            # ausschalten
            debug << "Switch off dxl_power"
            # das sleep hier ist nötig da es sonst zu fehlern in der
            # firmware der Motoren kommt!
            # Vermutete ursache:
            # Schreiben der ROM area der Register mit sofortigen
            # abschalten des Stromes führt auf den motoren einen
            # vollst#ndigen Reset durch!
            time.sleep(0.3) # WICHTIGE CODEZEILE! (siehe oben)
            self.ctrl.write_register(ID_CM730, CM730.dxl_power, 0)
            self.dxl_power = False

cpdef bootstrap(device="/dev/ttyUSB0", ipc=None, dieflag=True, standupflag=True,
            softoff=False, softstart=False, starttest=False, cm_370=True):
    """ Mit dieser Methode kann ein :class:`MotionServer` für einen Roboter
        über die serielle Schnittstelle *device* hergestellt werden.
        Die Daten werden über einen SharedMemoryIPC bereitgestellt

        :param device: Serielles Device zu dem sich verbunden werden soll
            Wenn dieser Parameter ein Tupel ist, wird angenommen
            das es eine IP und Roboternummer für die Simulatorbridge ist.
        :type device: String oder Tupel
        :param ipc: Ein :class:`ipc` welches genutzt werden soll
        :type ipc: ipc
        :param dieflag: Ob die Motion sich nach 60 Sekunden inaktivität beenden
            soll.
        :type dieflag: Boolean
        :param standupflag: Ob der Roboter aufstehen soll
        :type standupflag: Boolean
        :param softoff: ob der Roboter in den Softoffstatus wechseln soll,
            anstad auszugehen
        :type softoff: Boolean
        :param softstart: Ob der roboter im Softoff modus starten soll
        :type softstart: Boolean
        :param starttest: Ob der Roboter beim Straten die Motoren suchen soll
        :type starttest: Boolean
        :param cm_370: If the Robot has a cm_370 or compatible board
        :type cm_370: Boolean
    """
    # Verbindung zur Hardware herstellen
    cdef int has_power
    debug << "Verbinde zur Hardware"
    try:
        ipc = ipc or SharedMemoryIPC(client=False)
        # prüfen ob ein Device String oder ein Tupel für die Simulation
        # übergeben wurde
        if isinstance(device, (tuple, list)):
            serial = Simulatorbridge("BitBots", device[1], ipc, device[0])
        else:
            serial = Serial(device)
        ctrl = Controller(serial)
    except Exception as e:
        debug.warning("Fehler beim verbinden mit der Hardware aufgetreten: %s" % e)
        raise
    config = get_config()
    # anzahl der Motoren für diverse Kalibrierungen
    try:
        #wenn hier fehler auftreten sind wir verbunden und etwas anderes ist
        # nicht ganz wie es soll, aber kein grund neu zu conecten
        if cm_370:
            ctrl.write_register(ID_CM730, CM730.led_eye, (0, 255, 255))
            has_power = ctrl.read_register(ID_CM730, CM730.dxl_power)
        else:
            has_power = True  # if there is no controlboard for power we asume power is on
        motors = config[config['RobotTypeName']]['motors']

        if starttest or config['setMXRom'] and not has_power:
            ctrl.write_register(ID_CM730, CM730.dxl_power, 1)
            time.sleep(0.3)

        if starttest:
            # anpingen aller Motoren
            debug.log("Pinge Motoren")
            if cm_370:
                ctrl.write_register(ID_CM730, CM730.led_head, (0, 255, 0))
            all_motors = True
            missing_motors = []
            for i in motors:
                try:
                    if not ctrl.ping(i):
                        # Motor nicht gefunden
                        missing_motors.append(i)
                        debug.warning("Motor %d nicht gefunden" % i)
                        all_motors = False
                except MotorError as e:
                    debug.error(e, 'Error while pinging motors, try to continue: ')

            if not all_motors:
                say("WARNING! Cable Error!")
                msg = MotorConnectionAnalyser().get_error_message(
                    missing_motors)
                say(msg)
                if len(missing_motors) == len(motors):
                    say("I found no motor at all, I am missing number 1 to %i" % motors[-1])
                else:
                    say("The following motors are Missing: %s" %
                        "".join(["%d, " % i for i in missing_motors]))
                debug.warning(msg)
                say("Please check my cables!")
                debug.warning("Es fehlen Motoren, sysexit!")
                if cm_370:
                    ctrl.write_register(ID_CM730, CM730.dxl_power, 0)
                exit()

        # setze Motorregister neu
        if config['setMXRom']:
            debug << "Set Motor ROM"
            if cm_370:
                ctrl.write_register(ID_CM730, CM730.led_head, (255, 0, 0))
            romsettings = config['mx28config']['ROM']
            for i in motors:
                ctrl.write_register(i,MX28.led, 1)
                for conf in romsettings:
                    ctrl.write_register(i,MX28.get_register_by_name(conf),
                        romsettings[conf])
                ctrl.write_register(i,MX28.led, 0)
            debug << "Rom der Motoren gesetzt"

        if not (softstart):
            # wenn wir soft starten wollen müssen wir den power garnicht
            # erst anmachen
            ctrl.write_register(ID_CM730, CM730.dxl_power, 1)
        else:
            # falls der strom an ist machen wir ihn wieder aus
            if has_power:
                # wenn der Strom an war lassen wir ihn an, dann starten wir
                # vermutlich nur kurz neugestartet
                softstart = False
                # wir setzen softart off da wir schon stromm haben
            else:
                # früher haben wir hier den strom ausgemacht, der
                # basemotionserver prüft das nun aber selber, und
                # wir können hier Zeit Sparen
                pass

        # Augenfarbe setzen
        if cm_370:
            ctrl.write_register(ID_CM730, CM730.led_eye, (0, 255, 0))
            ctrl.write_register(ID_CM730, CM730.led_head, (0, 255, 0))
            #print "CM730 Firmware Version:", ctrl.read_register(ID_CM730, CM730.version)
            #print "MX28 Firmware Version:", ctrl.read_register(1, MX28.version)
    except IOError as e:
        debug.error(e, "Es ist ein fehler beim init der Motion aufgetreten, " +
        "Versuche weiterzumachen")
    try:
        # Server starten
        debug << "Start Motionserver"
        ms = MotionServer(ipc, ctrl, dieflag, standupflag, softoff, softstart, cm_370)
        run(ms)
    except StandardError as e:
        debug.error(e, "Motion had an Error:")
        raise
    finally:
        debug << "Shutdown"
        try:
            # Augenfarbe setzen
            if cm_370:
                ctrl.write_register(ID_CM730, CM730.led_eye, (255, 0, 0))
                ctrl.write_register(ID_CM730, CM730.led_head, (0, 255, 0))
        except:
            pass

        time.sleep(1)
        try:
            for i in motors:
                ctrl.write_register(i, MX28.torque_enable, 0)
            if cm_370:
                ctrl.write_register(ID_CM730, CM730.dxl_power, 0)
        except:
            pass
