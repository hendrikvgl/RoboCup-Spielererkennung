# -*- coding: utf-8 -*-
from libcpp cimport bool
import numpy as np
cimport numpy as np
np.import_array()
import time
from bitbots.kick.functionWrapper cimport SingleArgFunctionWrapper, DoubleArgFunctionWrapper, ValidateFunctionWrapper
from bitbots.robot.pypose cimport PyPose as Pose
from bitbots.robot.kinematics cimport Robot
from bitbots.kick.bezier cimport Bezier

cdef class Phase(object):

    def __cinit__(self, Robot robot, DoubleArgFunctionWrapper dist_func, SingleArgFunctionWrapper cog_func, \
                SingleArgFunctionWrapper cog_dist_func, ValidateFunctionWrapper val_func, np.ndarray start, np.ndarray target, \
                np.ndarray prev_dir=None, np.ndarray direction=None, int max_iter=100, bool no_cog=False):
        """Konstruktor zur Erzeugung einer Phase. """
        self.delta = 0.1              # Winkel-Delta bei der Iteration
        self.epsilon = 0.005          # Fehlergrenze

        self.robot = robot            # Modell des Roboters zum Bestimmen der
                                      # Gliedpositionen

        self.distance = dist_func     # Funktionen zur Bewertung der Distanz und des
        self.cog = cog_func           # Masseschwerpunktes
        self.cog_distance = cog_dist_func
        self.validate = val_func

        self.max_iter = max_iter      # maximale Anzahl an Iterationen

        self.no_cog = no_cog          # Gibt an, ob der Masseschwerpunkt
                                      # beruecksichtigt werden soll
        self.iter = []                # Informationen ueber die einzelnen Iterationen
                                      # zu Debug-Zwecken
        cdef np.ndarray base
        if prev_dir is None:
            # keine vorherige Bezierkurve vorhanden
            base = (np.array(target) - start) / 3 + start
        else:
            # Vorherige Bezierkurve muss beruecksichtigt werden
            base = 2 * np.array(start) - prev_dir

        if direction is None:
            # kein dritter Stuetpunkt angegeben
            direction = 2 * (np.array(target) - start) / 3 + start
        self.direction = direction

        self.bezier = Bezier(start,base,direction,target)

    cdef np.ndarray get_direction(self):
        return self.direction

    cdef Bezier get_bezier(self):
        return self.bezier

    cdef list get_iter(self):
        return self.iter

    cdef Pose calc_angles(self,Pose ipc_pose, float t):
        """
        Bestimmt nummerisch die Winkelkonstellation der Gelenke,
        um aus der gegebenen Anfangsstellung die angegebenen Zielkoordinaten zu erreichen.
        """
        # Bestimme die zu erreichende Position
        cdef np.ndarray dest = np.array(self.bezier.pos(t))

        self.robot.update(ipc_pose)
        self.robot.inverse_chain(3, dest)
        self.robot.set_angles_to_pose(ipc_pose, 3)
        self.iter.append(1)

        return ipc_pose
        """
        # Lese die Winkel aus der momentanen Pose aus
        cdef np.ndarray angles = pose_to_array(ipc_pose)

        # Aktualisiere interne Repraesentation des Roboters
        self.robot.update_with_matrix(angles)

        # Messungen zu Debug-Zwecken
        cdef float start = time.time()

        # Finde Winkelkonstellation bei der der Abstand zum Ziel
        # unter einem bestimmten Schwellenwert liegt
        cdef float error = self.distance.apply(self.robot, dest)
        cdef np.ndarray a
        cdef int i = 0
        while error >= self.epsilon and i < self.max_iter:
            # Minimiere Abstand
            a = np.array(self.step(angles, dest, error))
            angles -= a

            # Wirkung ueberpruefen
            self.robot.update_with_matrix(angles)
            error = self.distance.apply(self.robot, dest)
            i += 1

        # Messung zu Debug-Zwecken
        self.iter.append(i)
        end = time.time()
        with open('plot/iters', 'a') as f:
            f.write('calc time: %.3f, iterations: %i\n' % (end - start, i))
        print 'calc time: %.3f, iterations: %i' % (end - start, i)

        return array_to_pose(angles)
        """

    cdef np.ndarray step(self, np.ndarray angles, np.ndarray dest, float error):
        """Liefert Winkeländerung der Gelenke, die den Abstandes zum Ziel möglichst maximal verringert."""
        #cdef  list correction = []
        cdef np.ndarray correction = np.empty(len(angles))

        # Stabilitaet der Pose des Roboters
        cdef float cog_error = self.cog.apply(self.robot)

        # Finde das Minimum der Abstandsfunktion in Abhängigkeit der Gelenkwinkel.
        # Bilde dazu mit Hilfe des Differenzenquotienten die erste Ableitung
        # an der Stelle der momentanen Gelenkwinkel. Der Gradient wird genutzt um
        # sich in Richtung des Mimimums zu bewegen.
        cdef float angle
        cdef float p1, p2, m1, m2
        cdef float p_err, m_err
        cdef float cor
        cdef bool v1, v2
        for index in xrange(len(angles)):
            # Speicher initiale Winkelstellung
            angle = angles[index]

            # Bestimme Abstand an der Position Winkel - Delta
            angles[index] = angle - self.delta
            self.robot.update_with_matrix(angles)
            v1 = self.validate.apply(self.robot)
            p1 = self.distance.apply(self.robot, dest)
            m1 = self.cog_distance.apply(self.robot)

            # Bestimme Abstand an der Position Winkel + Delta
            angles[index] = angle + self.delta
            self.robot.update_with_matrix(angles)
            v2 = self.validate.apply(self.robot)
            p2 = self.distance.apply(self.robot, dest)
            m2 = self.cog_distance.apply(self.robot)

            # Setze Winkel zurück auf initialen Wert
            angles[index] = angle

            # Berechne Differenzenquotient
            if cog_error < 0.3 or self.no_cog:
                # Pose ist stabil, Abstand zum Ziel wird minimiert
                cor = (p2 - p1) / (2 * self.delta)
            else:
                # Pose droht umzukippe, Masseschwerpunkt wird dem
                # Zentrum des Stabilitaetsgebiets genaehert
                cor = (m2 - m1) / (2 * self.delta)

            if (cor > 0 and v2 == True) or (cor < 0 and v1 == True):
                # Pose ist physikalisch moeglich
                #correction.append(cor)
                correction[index] = cor
            else:
                # Pose laesst sich vom realen Roboter nicht einnehmen
                #correction.append(0)
                correction[index] = 0
        # Gewichte den Gradienten um eine Oszillation zu vermeiden
        return normalize_vector(np.array(correction), error)

cdef np.ndarray normalize_vector(np.ndarray  correction, float error, float weight=0.03):
    """Gewichtet den übergebenen Gradienten um zu verhindern, dass
    die Gelenkkette um die Zielposition oszilliert."""
    # normiere Gradienten auf die Länge 1
    #if sum(correction) != 0:
    #    correction = correction /np.linalg.norm(correction)

    correction = weight * correction
    return correction

cdef np.ndarray pose_to_array(Pose ipc_pose):
    """Wandelt eine Pose in eine Liste aus Winkeln um"""
    return np.asarray([
        radians(ipc_pose.r_shoulder_pitch.position),
        radians(ipc_pose.l_shoulder_pitch.position),
        radians(ipc_pose.r_shoulder_roll.position),
        radians(ipc_pose.l_shoulder_roll.position),
        radians(ipc_pose.r_elbow.position),
        radians(ipc_pose.l_elbow.position),

        radians(ipc_pose.r_hip_yaw.position),
        radians(ipc_pose.l_hip_yaw.position),
        radians(ipc_pose.r_hip_roll.position),
        radians(ipc_pose.l_hip_roll.position),
        radians(ipc_pose.r_hip_pitch.position),
        radians(ipc_pose.l_hip_pitch.position),
        radians(ipc_pose.r_knee.position),
        radians(ipc_pose.l_knee.position),
        radians(ipc_pose.r_ankle_pitch.position),
        radians(ipc_pose.l_ankle_pitch.position),
        radians(ipc_pose.r_ankle_roll.position),
        radians(ipc_pose.l_ankle_roll.position),

        radians(ipc_pose.head_pan.position),
        radians(ipc_pose.head_tilt.position)
    ], dtype=np.float32)

cdef Pose array_to_pose(np.ndarray array):
    """Wandelt eine Liste aus Winkeln um in eine Pose"""
    pose = Pose()

    pose.r_shoulder_pitch.goal = degrees(array[0])
    pose.l_shoulder_pitch.goal = degrees(array[1])
    pose.r_shoulder_roll.goal = degrees(array[2])
    pose.l_shoulder_roll.goal = degrees(array[3])
    pose.r_elbow.goal = degrees(array[4])
    pose.l_elbow.goal = degrees(array[5])

    pose.r_hip_yaw.goal = degrees(array[6])
    pose.l_hip_yaw.goal = degrees(array[7])
    pose.r_hip_roll.goal = degrees(array[8])
    pose.l_hip_roll.goal = degrees(array[9])
    pose.r_hip_pitch.goal = degrees(array[10])
    pose.l_hip_pitch.goal = degrees(array[11])
    pose.r_knee.goal = degrees(array[12])
    pose.l_knee.goal = degrees(array[13])
    pose.r_ankle_pitch.goal = degrees(array[14])
    pose.l_ankle_pitch.goal = degrees(array[15])
    pose.r_ankle_roll.goal = degrees(array[16])
    pose.l_ankle_roll.goal = degrees(array[17])

    pose.head_pan.goal = degrees(array[18])
    pose.head_tilt.goal = degrees(array[19])

    for name, joint in pose:
        joint.position = joint.goal

    return pose

cdef class Phaseholer(object):
    """ Quick and Dirty schnelimplementation einer Cython linked list, damit beim
    ausführen des Kicks nicht in den Python kontext gewechselt wird, was unheimlich Performance kostet
    Ich bin zu müde um zu schreiben ...."""
    #cdef int num, idx
    #cdef Phase p
    #cdef Phaseholer next

    def __cinit__(self, Phase phase, int idx, int num):
        self.idx = idx
        self.num = num
        self.phase = phase
        self.next = None

    cdef Phase get(self, int idx):
        """ das Holen einer Phase geschieht durch selbstorganisiertes suchen dieser Klasse
        Ein Dekrementieren des suchindex geht schlecht, da die ein (-1) eine Sonderrolle hat"""
        if idx is self.idx:
            return self.phase
        elif self.next is None:
            return None
        else:
            return self.next.get(idx)

    cdef append(self, Phase phase):
        self.num = self.num + 1
        if self.next is None:
            self.next = Phaseholer(phase, self.idx + 1, self.num + 1)
        else:
            self.next.append(phase)

    cdef int get_num(self):
        return self.num

    cdef remove_first(self):
        """ Index -1 als Koordinator hat hier ne sonderrolle, das Entfernen des ersten wird einfach propagoert """
        if self.idx is -1:
            self.next = self.next.next
        else:
            self.idx = self.idx - 1
        self.num = self.num - 1
        if self.next is not None:
            self.next.remove_first()
