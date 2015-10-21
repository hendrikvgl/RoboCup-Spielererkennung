# -*- coding: utf-8 -*-
from libcpp cimport bool

import time
import Gnuplot
import numpy as np
cimport numpy as np
np.import_array()

from bitbots.robot.kinematics cimport Joint
from bitbots.robot.pypose cimport PyPose as Pose
from bitbots.robot.kinematics cimport Robot
from bitbots.ipc.ipc cimport SharedMemoryIPC
from bitbots.kick.kickIPC cimport SingleArgFunctionWrapper, DoubleArgFunctionWrapper, ValidateFunctionWrapper
from bitbots.kick.vector cimport orig, pitch, trans3d, distance
from bitbots.kick.kickIPC cimport Bezier
from bitbots.kick.kickIPC cimport Phase, Phaseholer


cdef class Kinematic(object):

    def __cinit__(self):
        """Konstruktor"""
        self.ipc = SharedMemoryIPC()    # IPC zum kommunizieren mit der Hardware
        self.robot = Robot()            # Modell des Roboters zum Bestimmen der Gliedpositionen
        self.robot.update(self.ipc.get_pose())

        #self.phases = []                # Phasen aus denen die Bewegung zusammengesetzt ist
        self.phases = Phaseholer(None, -1, 0)
        self.prev_dir = None            # 3ter Bezier-Stuetzpunkt der vorherigen Phase

    cdef kick(self, np.ndarray ball_pos, float kick_angle, bool rightfoot=True):
        """Laesst den Roboter eine einfache Schussbewegung ausfuehren. Diese Bewegung besteht aus einer Phase.
        Die dazugehoerige Bezierkurve beginnt bei der momentanen Position des Schussfusses und endet an der Ballposition.
        Durch den Winkel ist es moeglich, die Richtung zu manipulieren, aus der sich der Fuss zur Ballposition bewegt.
        Optional ist die angabe des Schussfusses. Im Normalfall wird der rechte Fuss genutzt. Die Koordinaten der Ballposition
        muessen zudem relativ zum Standfuss angegeben werden."""

        # Initialisiere das Modell mit der realen Roboterpose
        self.robot.update(self.ipc.get_pose())

        # Verschiebe das Roboterkoordinatensystem, so dass der Standfuss dem Nullpunkt entspricht
        # und bestimme die Position des Schussfusses
        cdef np.ndarray d
        if rightfoot is True:
            d = (self.robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * (self.robot.get_r_foot_endpoint().get_chain_matrix() * trans3d(z=0.052)))
        else:
            d = (self.robot.get_r_foot_endpoint().get_chain_matrix(inverse=True) * (self.robot.get_l_foot_endpoint().get_chain_matrix() * trans3d(z=0.052)))
        cdef np.ndarray pos = (d* orig())[:3,2:3]
        # Bestimme 3ten Bezier-Stuetzpunkt
        cdef np.ndarray p = pitch(radians(kick_angle))[:3,:3]
        cdef np.ndarray direction = ball_pos - ((p * (ball_pos - pos)) / 3)

        cdef DoubleArgFunctionWrapper dist_func = DoubleArgFunctionWrapper()
        cdef SingleArgFunctionWrapper mass_func = SingleArgFunctionWrapper()
        cdef SingleArgFunctionWrapper mass_dist_func = SingleArgFunctionWrapper()
        cdef ValidateFunctionWrapper val_func = ValidateFunctionWrapper()
        # Bestimme Masse- und Distanzfunktionen, je nach Standfuss
        dist_func.set(&kick_r_foot_distance) if rightfoot is True else dist_func.set(&kick_l_foot_distance)
        mass_func.set(&kick_r_foot_cog) if rightfoot is True else mass_func.set(&kick_l_foot_cog)
        mass_dist_func.set(&kick_r_foot_cog_distance) if rightfoot is True else mass_dist_func.set(&kick_l_foot_cog_distance)
        val_func.set(&kick_r_foot_validate) if rightfoot is True else val_func.set(&kick_l_foot_validate)

        self.add_phase(dist_func, mass_func, mass_dist_func, val_func, pos, ball_pos, direction)

    cdef add_phase(self, DoubleArgFunctionWrapper dist_func, SingleArgFunctionWrapper mass_func, SingleArgFunctionWrapper mass_dist_func, \
                    ValidateFunctionWrapper val_func, np.ndarray start, np.ndarray target, np.ndarray direction=None):
        """Fuegt der Bewegung eine weitere Phase hinzu. Dafuer muessen Start- und Zielposition uebergeben werden,
        sowie optional eine Position, aus deren Richtung sich der Zielposition genaehert werden soll.
        Guetefunktionen fuer Distanz und Masse muessen angegeben werden, mit deren Hilfe der Abstand des Schussfusses zum Zielpunkt und
        der Abstand des Masseschwerpunktes zum Zentrum des Stabilitaetsgebiet bewertet werden kann"""
        self.phases.append(Phase(self.robot, dist_func, mass_func, mass_dist_func, val_func, start, target, self.prev_dir, direction))
        #self.prev_dir = self.phases[-1].get_direction()
        self.prev_dir = self.phases.get(self.phases.get_num() - 1).get_direction()

    cdef execute(self):
        """Fuehrt alle vorhandene Phasen der Reihe nach aus."""
        self.phasenum = 0 # Phase-Nummer zu Debug-Zwecken
        cdef int iters
        #while len(self.phases) > 0:
        while self.phases.get_num() > 0:
            #self.executePhase(self.phases[0])
            self.executePhase(self.phases.get(0))

            # Debug Ausgabe
            #iters = sum(self.phases[0].get_iter())/float(len(self.phases[0].get_iter()))
            iters = sum(self.phases.get(0).get_iter())/float(len(self.phases.get(0).get_iter()))
            with open('plot/iters', 'a') as f:
                f.write("phase complete - average iteration: %.2f\n" % iters)
            print "phase complete - average iteration: %.2f" % iters
            self.phasenum += 1
            #self.phases = self.phases[1:]
            self.phases.remove_first()


    cdef executePhase(self, Phase phase, float t_total=7.0, float delta=0.25):
        """Führt eine Phase aus."""
        self.frame = 0  # Frame-Nummer zu Debug-Zwecken

        # Bewege Roboter zur Initialposition
        cdef float t = 0
        cdef Pose cur_pose = self.ipc.get_pose()
        cdef Pose next_pose = phase.calc_angles(cur_pose, t)
        self.update_pose(cur_pose, next_pose, delta)
        cdef float start = time.time()
        cdef float sleep
        while t < t_total:
            # Positionen auf der Bezierkurve abarbeiten
            t+= delta
            # Werte für die nächste Winkelangabe bestimmen
            next_pose = phase.calc_angles(next_pose, t/t_total)

            # Warten, wenn momentane Bewegung noch ausgefuehrt wird
            sleep = delta - (time.time() - start)
            if sleep > 0:
                time.sleep(sleep)
            start = time.time()

            # Winkel setzen
            cur_pose = self.ipc.get_pose()
            self.update_pose(cur_pose, next_pose, delta)

    cdef update_pose(self, Pose cur_pose, Pose new_pose, float delta):
        """Uebergibt dem Roboter eine Pose. Passt dabei
        die Winkelgeschwindigkeit der Zeit an, die fuer die Bewegung
        zur Verfuegung steht."""
        for name, joint in new_pose:
            # Winkelgeschwindigkeit ergibt sich aus der Zeit und der
            # Differenz zwischen momentanem Winkel und Zielwinkel
            joint.speed = abs(cur_pose[name].position - joint.goal) / delta

        # Pose dem Roboter uebergeben
        self.ipc.update(new_pose)
        print "Updated IPC Pose"

        cdef Robot robot = Robot()
        robot.update(new_pose)
        # Debug Ausgabe
        plot(robot,png=True,frame=self.frame, bezier=self.phases.get(0).get_bezier(), mass=self.robot.get_center_of_gravity(), gplot=False, ball_pos=None)
        self.frame += 1

cdef float kick_r_foot_cog(Robot robot):
    """Bewertet die Position des Masseschwerpunkts in Hinblick auf das Stabilitaetsgebiet.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der linke Fuss.
    Wenn der Masseschwerpunkt ausserhalb des Stabilitaetsgebiet liegt, ist der Rueckgabewert 1.
    Ansonsten liegt der Wert zwischen 0 und 1, wobei 0 den optimale Wert darstellt."""

    # Fusslaenge
    cdef float length=0.104 * 0.5
    cdef float cog_err
    cdef float width_err

    # Verschiebe Koordinatensystem, so dass der linke Fuss dem Ursprung entspricht
    cdef np.ndarray cog = np.empty(4)
    cog[:3] = robot.get_center_of_gravity()
    cog[3] = 1
    cog = (robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * cog)

    if cog[0].all() > 0.044 or cog[0].all() < -0.022 or abs(cog[2].all()) > length:
        # Masseschwerpunkt liegt ausserhalb der Fussflaeche
        cog_err = 1
    else:
        # Masseschwerpunkt liegt innerhalb der Fussflaeche
        width_err = cog[0].all()/0.044 if cog[0].all() > 0 else abs(cog[0].all())/0.022
        cog_err = width_err * ((abs(cog[2].all()) / length))
    return cog_err

cdef float kick_r_foot_cog_distance(Robot robot):
    """Bewertet den Abstand des Masseschwerpunkts zum Zentrum des Stabilitaetsgebiet.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der linke Fuss."""
    # Verschiebe Koordinatensystem, so dass der linke Fuss dem Ursprung entspricht
    cdef np.ndarray cog = np.empty(4)
    cog[:3] = robot.get_center_of_gravity()
    cog[3] = 1
    cog = (robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * cog)
    return cog[0,0] * cog[2,0]

cdef float kick_r_foot_distance(Robot robot, np.ndarray dest):
    """Bewertet den Abstand des Schussfusses zur Ballposition.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der linke Fuss."""
    # Verschiebe Koordinatensystem, so dass der linke Fuss dem Ursprung entspricht
    cdef np.ndarray d = (robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_r_foot_endpoint().get_chain_matrix() * trans3d(z=0.052)))
    d = (d * orig())
    return distance(d[:3,2:3], dest)

cdef bool kick_r_foot_validate(Robot robot):
    """Gibt an, ob die momentane Pose des uebergebenen Roboters auch in der
    Realitaet umgesetzt werden kann. Momentan wird lediglich sicher gestellt,
    dass sich der Schussfuss ueberhalb des Bodens befindet."""
    # Verschiebe Koordinatensystem, so dass der linke Fuss dem Ursprung entspricht
    cdef np.ndarray p1 = (robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_r_foot_endpoint().get_chain_matrix() * trans3d(x=0.044,y=0,z=0.052)))
    p1 = p1 * orig()
    cdef np.ndarray p2 = (robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_r_foot_endpoint().get_chain_matrix() * trans3d(x=-0.022,y=0,z=-0.052)))
    p2 = p2 * orig()
    return p1[1,0] >= -0.05 and p2[1,0] >= -0.05

cdef float kick_l_foot_cog(Robot robot):
    """Bewertet die Position des Masseschwerpunkts in Hinblick auf das Stabilitaetsgebiet.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der rechte Fuss.
    Wenn der Masseschwerpunkt ausserhalb des Stabilitaetsgebiet liegt, ist der Rueckgabewert 1.
    Ansonsten liegt der Wert zwischen 0 und 1, wobei 0 den optimale Wert darstellt."""

    # Dimension der Fussflaeche
    cdef float length=0.104 * 0.5
    cdef float cog_err, width_err

    # Verschiebe Koordinatensystem, so dass der rechte Fuss dem Ursprung entspricht
    cdef np.ndarray cog = np.empty(4)
    cog[:3] = robot.get_center_of_gravity()
    cog[3] = 1
    cog = robot.get_r_foot_endpoint().get_chain_matrix(inverse=True) * cog

    if cog[0] < -0.044 or cog[0] > 0.022 or abs(cog[2]) > length:
        # Masseschwerpunkt liegt ausserhalb der Fussflaeche
        cog_err = 1
    else:
        # Masseschwerpunkt liegt innerhalb der Fussflaeche
        width_err = abs(cog[0])/0.044 if cog[0] < 0 else cog[0]/0.022
        cog_err = width_err * ((abs(cog[2]) / length))
    return cog_err

cdef float kick_l_foot_cog_distance(Robot robot):
    """Bewertet den Abstand des Masseschwerpunkts zum Zentrum des Stabilitaetsgebiet.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der rechte Fuss."""
    # Verschiebe Koordinatensystem, so dass der rechte Fuss dem Ursprung entspricht
    cdef np.ndarray cog = np.empty(4)
    cog[:3] = robot.get_center_of_gravity()
    cog[3] = 1
    cog = robot.get_r_foot_endpoint().get_chain_matrix(inverse=True) * cog
    cog[1] = 0
    return np.linalg.norm(cog[:3])

cdef float kick_l_foot_distance(Robot robot, np.ndarray dest):
    """Bewertet den Abstand des Schussfusses zur Ballposition.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der rechte Fuss."""
    # Verschiebe Koordinatensystem, so dass der rechte Fuss dem Ursprung entspricht
    cdef np.ndarray d = (robot.get_r_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_l_foot_endpoint().get_chain_matrix() * trans3d(z=0.052)))
    d = d * orig()
    return distance(d[:3,2:3], dest)

cdef bool kick_l_foot_validate(Robot robot):
    """Gibt an, ob die momentane Pose des uebergebenen Roboters auch in der
    Realitaet umgesetzt werden kann. Momentan wird lediglich sicher gestellt,
    dass sich der Schussfuss ueberhalb des Bodens befindet."""
    # Verschiebe Koordinatensystem, so dass der rechte Fuss dem Ursprung entspricht
    cdef np.ndarray p1 = (robot.get_r_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_l_foot_endpoint().get_chain_matrix() * trans3d(x=0.044,y=0,z=0.052)))
    p1 = p1 * orig()
    cdef np.ndarray p2 = (robot.get_r_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_l_foot_endpoint().get_chain_matrix() * trans3d(x=-0.022,y=0,z=-0.052)))
    p2 = p2 * orig()
    return p1[1] >= -0.05 and p2[1] >= -0.05

cdef plot(Robot robot, np.ndarray ball_pos = None, bool png=False, int frame=0, Bezier bezier=None, np.ndarray mass=None, bool gplot=True):
    """Plottet den Roboter."""

    cdef np.ndarray inverse = robot.get_l_foot_endpoint().get_chain_matrix(inverse=True)
    cdef np.ndarray ep = np.empty(4)
    cdef np.ndarray p

    print "Right Leg Stuff:\n", (robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_r_foot_endpoint().get_chain_matrix() *
                                trans3d(x=0.044,y=0,z=0.052)))

    with open("plot/pos%i.gp" % frame, "w") as plotfile:

        for joint in robot.get_l_leg_chain():
            ep[:3] = joint.get_endpoint()
            ep[3] = 1
            p = inverse * ep
            plotfile.write("%f %f %f\n" % (float(p[0,0]), float(p[0,1]), float(p[0,2])))

        p = (robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_l_foot_endpoint().get_chain_matrix() * trans3d(z=0.052)))
        p = p * orig()
        plotfile.write("%f %f %f\n" % (float(p[0,0]), float(p[0,1]), float(p[0,2])))
        plotfile.write("\n")

        for joint in robot.get_r_leg_chain():
            ep[:3] = joint.get_endpoint()
            ep[3] = 1
            p = inverse * ep
            plotfile.write("%f %f %f\n" % (float(p[0,0]), float(p[0,1]), float(p[0,2])))

        p = (robot.get_l_foot_endpoint().get_chain_matrix(inverse=True) * (robot.get_r_foot_endpoint().get_chain_matrix() * trans3d(z=0.052)))
        p = p * orig()
        plotfile.write("%f %f %f\n" % (float(p[0,0]), float(p[0,1]), float(p[0,2])))
        plotfile.write("\n")

        for joint in robot.get_l_arm_chain():
            ep[:3] = joint.get_endpoint()
            ep[3] = 1
            p = inverse * ep
            plotfile.write("%f %f %f\n" % (float(p[0,0]), float(p[0,1]), float(p[0,2])))
        plotfile.write("\n")

        for joint in robot.get_r_arm_chain():
            ep[:3] = joint.get_endpoint()
            ep[3] = 1
            p = inverse * ep
            plotfile.write("%f %f %f\n" % (float(p[0,0]), float(p[0,1]), float(p[0,2])))
        plotfile.write("\n")

        plotfile.write("%f %f %f\n" % (0.044,0,0.052))
        plotfile.write("%f %f %f\n" % (-0.022,0,0.052))
        plotfile.write("%f %f %f\n" % (-0.022,0,-0.052))
        plotfile.write("%f %f %f\n" % (0.044,0,-0.052))
        plotfile.write("%f %f %f\n" % (0.044,0,0.052))
        plotfile.write("\n")

    if ball_pos is not None:
        with open("plot/ball.gp", "w") as plotfile:
            plotfile.write("%f %f %f\n" % tuple(ball_pos))
    else:
        open("plot/ball.gp","w") # remove old data

    if mass is not None:
        with open("plot/mass%i.gp" % frame, "w") as plotfile:
            print "Mass: ",mass
            ep[:3] = mass
            ep[3] = 1
            mass = inverse * ep
            plotfile.write("%f %f %f\n" % (float(mass[0,0]), float(mass[0,1]), float(mass[0,2])))
            plotfile.write("%f %f %f\n" % (float(mass[0,0]), 0.0, float(mass[0,2])))
    else:
        open("plot/mass%i.gp" % frame,"w") # remove old data

    if bezier is not None:
        bezier.visualize(100, only_data=True)
    else:
        open("plot/bezier_curve%i.gp" % frame,"w") # remove old data

    if gplot == True:
        g = Gnuplot.Gnuplot(debug=1)
        if png:
            g('set terminal png')
            g('set output "plot/output/kick%04i.png"' % frame)
            #g('set view 90,90')
        else:
            g('set terminal wxt persist')

        g('set nokey')
        g('set xrange [%.3f:%.3f]' % (-.3, .2))
        g('set yrange [%.3f:%.3f]' % (-.1, .5))
        g('set zrange [%.3f:%.3f]' % (-.2, .2))
        g('set ytics 50')
        g('set ztics 100')
        g('set size square')
        g('splot "plot/pos%i.gp" every :::0::0 with lines, "plot/pos%i.gp" every :::1::1 with lines, "plot/pos%i.gp" every :::2::2 with lines, "plot/pos%i.gp" every :::3::3 with lines, "plot/pos%i.gp" every :::4::4 with lines, "plot/ball.gp", "plot/bezier_curve%i.gp" with lines, "plot/mass%i.gp"' % tuple([frame] * 7))

def run():
    k = Kinematic()
    pose = k.ipc.get_pose()
    #pose.l_hip_roll.goal = 13
    #pose.r_hip_roll.goal = 13
    #pose.l_ankle_roll.goal = 13
    #pose.r_ankle_roll.goal = 13
    #pose.l_hip_roll.speed = 5.0
    #pose.r_hip_roll.speed = 5.0
    #pose.l_ankle_roll.speed = 5.0
    #pose.r_ankle_roll.speed = 5.0


    #pose.l_ankle_pitch.goal = 45
    #pose.l_ankle_pitch.speed = 2

    #pose.r_ankle_pitch.goal = 0
    #pose.r_ankle_pitch.speed = 2

    print 'moving'
    k.ipc.update(pose)
    for i in range(5):
        print 5-i
        time.sleep(1)
    cdef np.ndarray l_foot = k.robot.get_l_foot_endpoint().get_endpoint()
    cdef np.ndarray r_foot = k.robot.get_r_foot_endpoint().get_endpoint()
    cdef np.ndarray ball_pos = -r_foot - l_foot
    ball_pos[1] = 0.05
    ball_pos[2] = 0.15
    k.kick(ball_pos, 0)
    print "Erste Phase gesetzt"

    cdef np.ndarray pos2 = np.array(ball_pos)
    pos2[1] = 0.00
    pos2[2] = 0.00
    cdef Robot robot = Robot()
    #robot.update(pose)
    k.kick(pos2, 0, True)
    print "Zweite Phase gesetzt"
    print 'kick ready'
    print "Ziele"
    print ball_pos
    print "Nummer 2"
    print pos2
    k.execute()
    #plot(k.robot, ball_pos=ball_pos, bezier=k.phases[0].bezier, mass=k.robot.get_center_of_gravity())
