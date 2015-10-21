# -*- coding: utf8 -*-

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.utility cimport pair
from libcpp cimport bool

from libc.stdlib cimport free

from cython.operator cimport dereference as deref
from cython.operator cimport address as ref

from bitbots.robot.pose cimport Pose
from bitbots.robot.pypose cimport PyPose, wrap_pose, wrap_pose_ref, wrap_pose_obj

from bitbots.util.datavector cimport DataVector, IntDataVector
from bitbots.util.pydatavector cimport PyDataVector, wrap_data_vector, PyIntDataVector, wrap_int_data_vector

from bitbots.ipc.ipcprovider cimport IPCProvider
from bitbots.ipc.ipcprovider cimport SharedMemoryIPCProvider

import numpy as np
cimport numpy as np
np.import_array()

import warnings

# aus basemotionserver.pxd
cdef public enum:
    STATE_CONTROLABLE = 1
    STATE_FALLING
    STATE_FALLEN
    STATE_GETTING_UP
    STATE_ANIMATION_RUNNING
    STATE_BUSY
    STATE_STARTUP
    STATE_PENALTY
    STATE_PENALTY_ANIMANTION
    STATE_RECORD
    STATE_SOFT_OFF
    STATE_WALKING

cdef class AbstractIPC:
    def __init__(self, client=True):
        if self.__class__ is AbstractIPC:
            raise ValueError("You cannot instantiate this class directly")

        self.force = AnimationLock(self)
        self.record = RecordLock(self)

    cpdef int get_version(self):
        """ Gibt die Versionsnummer der Pose zurück. Diese wird bei jedem
            Aufruf von :func:`update()` erhöht.
        """
        return self.ipc.get_version()

    cpdef PyPose get_pose(self):
        """ Gibt die aktuell gesetzte Pose des Roboters zurück.
            Es wird eine Kopie zurückgegeben, Änderungen an der Pose
            beeinflussen also nicht den Stand des Roboters
        """
        return wrap_pose_obj(<Pose>self.ipc.get_pose())

    cpdef PyPose get_pose_ref(self):
        """ Gibt die aktuell gesetzte Pose des Roboters zurück.
            Es wird jedoch keine Kopie, sondern eine Referenz auf die
            Pose des Roboters zurückgegeben.

            Achtung: Es empfielt sich, den IPC vorher zu 'locken'.
            with ipc:
                pose = ipc.get_pose_ref()
                pose.set_active(False)

        """
        return wrap_pose_ref(<Pose&>self.ipc.get_pose_ref())

    cpdef update(self, PyPose pose):
        """ Updated die Pose im Speicher. Es werden alle neu gesetzten
            *goal*- und *speed*-Werte übernommen. Alle anderen
            Gelenke und Werte werden ignoriert
        """
        if pose is None:
            raise ValueError("Pose can not be None")

        self.ipc.update(deref(pose.get_pose_ptr()))

    cpdef update_positions(self, PyPose pose):
        """ Updated nur die *position*-Felder aller Gelenke """
        if pose is None:
            raise ValueError("Pose can not be None")

        self.ipc.update_positions(deref(pose.get_pose_ptr()))

    cpdef PyIntDataVector get_gyro(self):
        """ Gibt den Wert des Gyrometers als :class:`PyIntDataVector`
            Instanz zurück
        """
        cdef IntDataVector dv = self.ipc.get_gyro()
        return wrap_int_data_vector(dv)

    cpdef set_gyro(self, PyIntDataVector dv):
        """ Setzt den Wert des Gyrometers. """
        if dv is None:
            raise ValueError("gyro can not be None")

        self.ipc.set_gyro(deref(dv.get_data_vector()))

    cpdef PyDataVector get_robot_angle(self):
        """ Gibt den Wert des Getrackten Gyrowertes als :class:`PyDataVector`
            Instanz zurück
        """
        cdef DataVector dv = self.ipc.get_robot_angle()
        return wrap_data_vector(dv)

    cpdef set_robot_angle(self, PyDataVector dv):
        """ Setzt den Wert des getrackten Gyrowertes. """
        if dv is None:
            raise ValueError("angle can not be None")

        self.ipc.set_robot_angle(deref(dv.get_data_vector()))

    cpdef PyIntDataVector get_accel(self):
        """ Gibt den Wert des Beschleunigungs-Sensors als :class:`PyIntDataVector`
            Instanz zurück
        """
        cdef IntDataVector dv = self.ipc.get_accel()
        return wrap_int_data_vector(dv)

    cpdef set_accel(self, PyIntDataVector dv):
        """ Setzt den Wert des Beschleunigungs-Sensors """
        if dv is None:
            raise ValueError("accel can not be None")

        self.ipc.set_accel(deref(dv.get_data_vector()))

    cpdef PyDataVector get_eye_color(self):
        """ Gibt die Augenfarbe des Roboters zurück """
        cdef DataVector dv = self.ipc.get_eye_color()
        return wrap_data_vector(dv)

    cpdef set_eye_color(self, PyDataVector dv):
        """ Setzt die Augenfarbe des Roboters """
        if dv is None:
            raise ValueError("eye_color can not be None")

        self.ipc.set_eye_color(deref(dv.get_data_vector()))

    cpdef PyDataVector get_forehead_color(self):
        """ Gibt die Farbe der LED auf der Stirn des Roboters zurück """
        cdef DataVector dv = self.ipc.get_forehead_color()
        return wrap_data_vector(dv)

    cpdef set_forehead_color(self, PyDataVector dv):
        """ Setzt die Farbe der LED auf der Stirn des Roboters """
        if dv is None:
            raise ValueError("forehead_color can not be None")

        self.ipc.set_forehead_color(deref(dv.get_data_vector()))

    cpdef set_state(self, int state):
        """ Mit dieser Methode kann dem Motion-Server ein Zustand des
            Roboters mitgeteilt werden. Zum Beispiel kann so das automatische
            Aufstehen wärend einer Animation deaktiviert werden. Oder jegliche
            Bewegungen können verhindert werden, indem der Zustand auf
            *PENALIZED* gesetzt wird.
        """
        self.ipc.set_state(state)

    cpdef int get_state(self):
        """ Gibt den in :func:`set_state` gesetzen Zustand zurück """
        return self.ipc.get_state()

    cpdef set_button1(self, bool state):
        """ Setzt den status des Button 1"""
        self.ipc.set_button1(state)

    cpdef bool get_button1(self):
        """ Gibt den in :func:`set_button1` gesetzen Zustand zurück """
        return self.ipc.get_button1()

    cpdef set_button2(self, bool state):
        """ Setzt den status des Button 2"""
        self.ipc.set_button2(state)

    cpdef bool get_button2(self):
        """ Gibt den in :func:`set_button2` gesetzen Zustand zurück """
        return self.ipc.get_button2()

    cpdef set_motion_state(self, int state):
        """ Über diese Funktion kann der Motion-Server unabhängig von
        des vom Nutzer über :func:`set_state` gesetzten Zustands einen
        eigenen Zustand setzen.

        Dieser enthält beispielsweise Informationen darüber, ob der Roboter
        momentan vom Nutzer steuerbar ist, oder nicht. Dies ist nicht der
        Fall, wenn der Motion-Server den Roboter aufstehen lässt.
        """
        self.ipc.set_motion_state(state)

    cpdef int get_motion_state(self):
        """ Gibt den in :func:`set_motion_state` gesetzten Zustand zurück """
        return self.ipc.get_motion_state()

    cpdef set_walking_forward(self, int speed):
        """Setzt die Walkinggeschwindigkeit für forward"""
        self.ipc.set_walking_forward(speed)

    cpdef int get_walking_forward(self):
        """Gibt die Walkingeschwindigkeit für forward"""
        return self.ipc.get_walking_forward()

    cpdef set_walking_sidewards(self, int speed):
        """Setzt die Walkinggeschwindigkeit für sidewards"""
        self.ipc.set_walking_sidewards(speed)

    cpdef int get_walking_sidewards(self):
        """Holt die geschwindigkeit fürs Walking sidewards"""
        return self.ipc.get_walking_sidewards()

    cpdef set_walking_angular(self, int speed):
        """Setzt die Walkinggeschwindigkeit sidewards"""
        self.ipc.set_walking_angular(speed)

    cpdef int get_walking_angular(self):
        """Gibt die waklinggeschwindigkeit für sidewards"""
        return self.ipc.get_walking_angular()

    cpdef set_walking_activ(self, bool state):
        """Setzt den Walking Aktiv Status. Bei False wird nicht gelaufen"""
        self.ipc.set_walking_activ(state)

    cpdef int get_walking_foot_phase(self):
        """Gibt das Standbein zurück"""
        return int(self.ipc.get_walking_foot_phase())

    cpdef set_walking_foot_phase(self, unsigned char phase):
        """Setzt das Standbein"""
        self.ipc.set_walking_foot_phase(phase)

    cpdef bool get_walking_activ(self):
        """Gibt den zurück ob der roboter laufen soll"""
        return self.ipc.get_walking_activ()

    cpdef reset_tracking(self):
        """Weißt die Motion an das tracking zu resetten"""
        self.ipc.reset_tracking()

    cpdef bool get_reset_tracking(self):
        """Fragt ab ob ein reset fürs Tracking gefordert wird, flag wird
        dabei zurückgesetzt"""
        return self.ipc.get_reset_tracking()

    cpdef PyDataVector get_last_track(self):
        """Die bewegung des Roboters vom vorletzten bis zum letzten reset
        als (x, y, z) wobei z die drehung repräsentiert"""
        cdef DataVector dv = self.ipc.get_last_track()
        return wrap_data_vector(dv)

    cpdef set_last_track(self, PyDataVector track):
        """Setzt den last_track"""
        self.ipc.set_last_track(deref(track.get_data_vector()))

    cpdef PyDataVector get_track(self):
        """Die bewegung des Roboters seit dem letztem reset als
        (x, y, z) bei z= orientierung"""
        cdef DataVector dv = self.ipc.get_track()
        return wrap_data_vector(dv)

    cpdef set_track(self, PyDataVector track):
        """Setzt die bewegung des Roboters"""
        self.ipc.set_track(deref(track.get_data_vector()))

    cpdef int get_last_track_time(self):
        """letzte zeit des resetes als unix timestamp"""
        return self.ipc.get_last_track_time()

    cpdef set_last_track_time(self, int time):
        """setzt die letzte resettime"""
        self.ipc.set_last_track_time(time)

    cpdef set_image(self, int width, int height, np.ndarray image):
        """
        Schreibt ein Bild in das IPC
        Usecase: In der Simulation kommen die Images im motionserver an
        """
        cdef char *data = np.PyArray_BYTES(image)
        self.ipc.set_image(width, height, data)

    cpdef np.ndarray get_image(self):
        """
        Hohlt ein mit `func`:set_image gesetztes Bild wieder aus dem Speicher
        """
        cdef np.npy_intp dim
        dim = self.ipc.get_image_width() * self.ipc.get_image_height() * 3
        cdef char * img = self.ipc.get_image()
        image = np.PyArray_SimpleNewFromData(1, &dim, np.NPY_UINT8, img)
        free(img)
        # kopieren da sonst auf daten im ipc gearbeitet wird
        #print image, image.shape, (self.ipc.get_image_height(), self.get_image_width(), 3), (self.ipc.get_image_height()* self.get_image_width()* 3)
        return np.reshape(image.copy(), (self.ipc.get_image_height(), self.get_image_width() * 3))#, order='C')


    cpdef int get_image_width(self):
        return self.ipc.get_image_width()

    cpdef int get_image_height(self):
        return self.get_image_height()

    property controlable:
        """ Gibt an, ob der Roboter vom Nutzer steuerbar ist.
            Dies ist der Fall wenn :func:`get_motion_state` auf
            *STATE_CONTROLABLE* gesetzt ist.
        """
        def __get__(self): return self.get_motion_state() == STATE_CONTROLABLE

    property is_recording:
        """ Gibt an, ob der Roboter im Record status ust.
            Dies ist der Fall wenn :func:`get_motion_state` auf
            *STATE_RECORD* gesetzt ist.
        """
        def __get__(self): return self.get_motion_state() == STATE_RECORD

    property forehead_color:
        """ Property für die LED Farbe auf der Stirn. Nimmt neben einem
            :class:`PyDataVector` auch ein :class:`tuple` oder :class:`list`
            an
        """
        def __get__(self): return self.get_forehead_color()
        def __set__(self, val):
            if isinstance(val, PyDataVector):
                self.set_forehead_color(val)
            else:
                self.set_forehead_color(PyDataVector(*val))

    property eye_color:
        """ Property für die LED Farbe der Augen. Nimmt neben einem
            :class:`PyDataVector` auch ein :class:`tuple` oder :class:`list`
            an
        """
        def __get__(self): return self.get_forehead_color()
        def __set__(self, val):
            if isinstance(val, PyDataVector):
                self.set_eye_color(val)
            else:
                self.set_eye_color(PyDataVector(*val))

    def __enter__(self):
        #self.ipc.lock()
        self.ipc.lock_pose()

    def __exit__(self, *ignore):
        #self.ipc.unlock()
        self.ipc.unlock_pose()


cdef class SharedMemoryIPC(AbstractIPC):
    def __cinit__(self, *args, **kwargs):
        self.ipc = <IPCProvider*>(new SharedMemoryIPCProvider())

    def __dealloc__(self):
        del self.ipc


cdef class AnimationLock(object):
    cdef AbstractIPC ipc
    cdef int prev

    def __init__(self, ipc):
        self.ipc = ipc
        self.prev = STATE_CONTROLABLE

    def __enter__(self):
        with self.ipc:
            self.prev = self.ipc.get_state()
            self.ipc.set_state(STATE_ANIMATION_RUNNING)

    def __exit__(self, *a):
        self.ipc.set_state(self.prev)

cdef class RecordLock(object):
    cdef AbstractIPC ipc
    cdef int prev

    def __init__(self, ipc):
        self.ipc = ipc
        self.prev = STATE_CONTROLABLE

    def __enter__(self):
        with self.ipc:
            self.prev = self.ipc.get_state()
            self.ipc.set_state(STATE_RECORD)

    def __exit__(self, *a):
        if self.prev == STATE_RECORD:
            self.prev = STATE_CONTROLABLE
        self.ipc.set_state(self.prev)


class NotControlableError(Exception):
    pass

