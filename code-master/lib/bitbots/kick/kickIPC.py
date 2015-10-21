# -*- coding: utf-8 -*-
#from bitbots.kick.kickIPC import run
def run(): pass

import math
#import vector as v
v=[]
#from phaseIPC import Phase
Phase=[]
import numpy as np
from bitbots.ipc import SharedMemoryIPC
from bitbots.robot.kinematics import Robot
import time
#import Gnuplot

run()

class KinematicDurchMergeWiederHierZumVergleichenDerImplementationen(object):

    def __init__(self):
        """Konstruktor"""
        self.ipc = SharedMemoryIPC()    # IPC zum kommunizieren mit der Hardware
        self.robot = Robot()            # Modell des Roboters zum Bestimmen der Gliedpositionen
        self.robot.update(self.ipc.get_pose())

        self.phases = []                # Phasen aus denen die Bewegung zusammengesetzt ist
        self.prev_dir = None            # 3ter Bezier-Stuetzpunkt der vorherigen Phase

    def kick(self, ball_pos, kick_angle, foot='right'):
        """Laesst den Roboter eine einfache Schussbewegung ausfuehren. Diese Bewegung besteht aus einer Phase.
        Die dazugehoerige Bezierkurve beginnt bei der momentanen Position des Schussfusses und endet an der Ballposition.
        Durch den Winkel ist es moeglich, die Richtung zu manipulieren, aus der sich der Fuss zur Ballposition bewegt.
        Optional ist die angabe des Schussfusses. Im Normalfall wird der rechte Fuss genutzt. Die Koordinaten der Ballposition
        muessen zudem relativ zum Standfuss angegeben werden."""

        # Initialisiere das Modell mit der realen Roboterpose
        self.robot.update(self.ipc.get_pose())

        # Verschiebe das Roboterkoordinatensystem, so dass der Standfuss dem Nullpunkt entspricht
        # und bestimme die Position des Schussfusses
        if foot is 'right':
            d = np.dot(self.robot.get_l_foot_endpoint().get_chain_matrix(inverse=True), np.dot(self.robot.get_r_foot_endpoint().get_chain_matrix(), v.trans3d(z=0.052)))
        else:
            d = np.dot(self.robot.get_r_foot_endpoint().get_chain_matrix(inverse=True), np.dot(self.robot.get_l_foot_endpoint().get_chain_matrix(), v.trans3d(z=0.052)))
        pos = np.dot(d, v.orig)[:3]

        # Bestimme 3ten Bezier-Stuetzpunkt
        direction = ball_pos - np.dot(v.pitch(math.radians(kick_angle))[:-1,:-1], (ball_pos - pos) / 3)

        # Bestimme Masse- und Distanzfunktionen, je nach Standfuss
        dist_func = kick_r_foot_distance if foot is 'right' else kick_l_foot_distance
        mass_func = kick_r_foot_cog if foot is 'right' else kick_l_foot_cog
        mass_dist_func = kick_r_foot_cog_distance if foot is 'right' else kick_l_foot_cog_distance
        val_func = kick_r_foot_validate if foot is 'right' else kick_l_foot_validate

        self.add_phase(dist_func, mass_func, mass_dist_func, val_func, pos, ball_pos, direction)

    def add_phase(self, dist_func, mass_func, mass_dist_func, val_func, start, target, direction=None):
        """Fuegt der Bewegung eine weitere Phase hinzu. Dafuer muessen Start- und Zielposition uebergeben werden,
        sowie optional eine Position, aus deren Richtung sich der Zielposition genaehert werden soll.
        Guetefunktionen fuer Distanz und Masse muessen angegeben werden, mit deren Hilfe der Abstand des Schussfusses zum Zielpunkt und
        der Abstand des Masseschwerpunktes zum Zentrum des Stabilitaetsgebiet bewertet werden kann"""
        self.phases.append(Phase(self.robot, dist_func, mass_func, mass_dist_func, val_func, start, target, self.prev_dir, direction, no_cog=True))
        self.prev_dir = self.phases[-1].direction

    def execute(self):
        """Fuehrt alle vorhandene Phasen der Reihe nach aus."""
        self.phasenum = 0 # Phase-Nummer zu Debug-Zwecken
        while len(self.phases) > 0:
            self.executePhase(self.phases[0])

            # Debug Ausgabe
            iters = sum(self.phases[0].iter)/float(len(self.phases[0].iter))
            with open('plot/iters', 'a') as f:
                f.write("phase complete - average iteration: %.2f\n" % iters)
            print "phase complete - average iteration: %.2f" % iters
            self.phasenum += 1
            self.phases = self.phases[1:]

    def executePhase(self, phase, t_total=7.0, delta=1.0):
        """Führt eine Phase aus."""
        self.frame = 0  # Frame-Nummer zu Debug-Zwecken

        # Bewege Roboter zur Initialposition
        t = 0
        cur_pose = self.ipc.get_pose()
        next_pose = phase.calc_angles(cur_pose, t)
        self.update_pose(cur_pose, next_pose, delta)
        start = time.time()
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

    def update_pose(self, cur_pose, new_pose, delta):
        """Uebergibt dem Roboter eine Pose. Passt dabei
        die Winkelgeschwindigkeit der Zeit an, die fuer die Bewegung
        zur Verfuegung steht."""
        for name, joint in new_pose:
            # Winkelgeschwindigkeit ergibt sich aus der Zeit und der
            # Differenz zwischen momentanem Winkel und Zielwinkel
            joint.speed = abs(cur_pose[name].position - joint.goal) / delta

        # Pose dem Roboter uebergeben
        self.ipc.update(new_pose)

        # Debug Ausgabe
        plot(new_pose,png=True,frame=self.frame,phase=self.phasenum, bezier=self.phases[0].bezier, mass=self.robot.get_center_of_gravity(), gplot=False)
        self.frame += 1

def kick_r_foot_cog(robot):
    """Bewertet die Position des Masseschwerpunkts in Hinblick auf das Stabilitaetsgebiet.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der linke Fuss.
    Wenn der Masseschwerpunkt ausserhalb des Stabilitaetsgebiet liegt, ist der Rueckgabewert 1.
    Ansonsten liegt der Wert zwischen 0 und 1, wobei 0 den optimale Wert darstellt."""

    # Verschiebe Koordinatensystem, so dass der linke Fuss dem Ursprung entspricht
    cog = np.empty(4)
    cog[:3] = robot.get_center_of_gravity()
    cog[3] = 1
    cog = np.dot(robot.get_l_foot_endpoint().get_chain_matrix(inverse=True), cog)

    # Fusslaenge
    length=0.104 * 0.5

    if cog[0] > 0.044 or cog[0] < -0.022 or abs(cog[2]) > length:
        # Masseschwerpunkt liegt ausserhalb der Fussflaeche
        cog_err = 1
    else:
        # Masseschwerpunkt liegt innerhalb der Fussflaeche
        width_err = cog[0]/0.044 if cog[0] > 0 else abs(cog[0])/0.022
        cog_err = width_err * ((abs(cog[2]) / length))
    return cog_err

def kick_r_foot_cog_distance(robot):
    """Bewertet den Abstand des Masseschwerpunkts zum Zentrum des Stabilitaetsgebiet.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der linke Fuss."""
    # Verschiebe Koordinatensystem, so dass der linke Fuss dem Ursprung entspricht
    cog = np.empty(4)
    cog[:3] = robot.get_center_of_gravity()
    cog[3] = 1
    cog = np.dot(robot.get_l_foot_endpoint().get_chain_matrix(inverse=True), cog)
    cog[1] = 0
    return np.linalg.norm(cog[:3])

def kick_r_foot_distance(robot, dest):
    """Bewertet den Abstand des Schussfusses zur Ballposition.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der linke Fuss."""
    # Verschiebe Koordinatensystem, so dass der linke Fuss dem Ursprung entspricht
    d = np.dot(robot.get_l_foot_endpoint().get_chain_matrix(inverse=True), np.dot(robot.get_r_foot_endpoint().get_chain_matrix(), v.trans3d(z=0.052)))
    d = np.dot(d, v.orig)
    return v.distance(d[:3], dest)

def kick_r_foot_validate(robot):
    """Gibt an, ob die momentane Pose des uebergebenen Roboters auch in der
    Realitaet umgesetzt werden kann. Momentan wird lediglich sicher gestellt,
    dass sich der Schussfuss ueberhalb des Bodens befindet."""
    # Verschiebe Koordinatensystem, so dass der linke Fuss dem Ursprung entspricht
    p1 = np.dot(robot.get_l_foot_endpoint().get_chain_matrix(inverse=True), np.dot(robot.get_r_foot_endpoint().get_chain_matrix(), v.trans3d(x=0.044,z=0.052)))
    p1 = np.dot(p1, v.orig)
    p2 = np.dot(robot.get_l_foot_endpoint().get_chain_matrix(inverse=True), np.dot(robot.get_r_foot_endpoint().get_chain_matrix(), v.trans3d(x=-0.022,z=-0.052)))
    p2 = np.dot(p2, v.orig)
    return p1[1] >= 0 and p2[1] >= 0

def kick_l_foot_cog(robot):
    """Bewertet die Position des Masseschwerpunkts in Hinblick auf das Stabilitaetsgebiet.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der rechte Fuss.
    Wenn der Masseschwerpunkt ausserhalb des Stabilitaetsgebiet liegt, ist der Rueckgabewert 1.
    Ansonsten liegt der Wert zwischen 0 und 1, wobei 0 den optimale Wert darstellt."""

    # Dimension der Fussflaeche
    length=0.104 * 0.5

    # Verschiebe Koordinatensystem, so dass der rechte Fuss dem Ursprung entspricht
    cog = np.empty(4)
    cog[:3] = robot.get_center_of_gravity()
    cog[3] = 1
    cog = np.dot(robot.get_r_foot_endpoint().get_chain_matrix(inverse=True), cog)

    if cog[0] < -0.044 or cog[0] > 0.022 or abs(cog[2]) > length:
        # Masseschwerpunkt liegt ausserhalb der Fussflaeche
        cog_err = 1
    else:
        # Masseschwerpunkt liegt innerhalb der Fussflaeche
        width_err = abs(cog[0])/0.044 if cog[0] < 0 else cog[0]/0.022
        cog_err = width_err * ((abs(cog[2]) / length))
    return cog_err

def kick_l_foot_cog_distance(robot):
    """Bewertet den Abstand des Masseschwerpunkts zum Zentrum des Stabilitaetsgebiet.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der rechte Fuss."""
    # Verschiebe Koordinatensystem, so dass der rechte Fuss dem Ursprung entspricht
    cog = np.empty(4)
    cog[:3] = robot.get_center_of_gravity()
    cog[3] = 1
    cog = np.dot(robot.get_r_foot_endpoint().get_chain_matrix(inverse=True), cog)
    cog[1] = 0
    return np.linalg.norm(cog[:3])

def kick_l_foot_distance(robot, dest):
    """Bewertet den Abstand des Schussfusses zur Ballposition.
    Standfuss und somit Ursprung des Koordinatensystem ist in diesem Fall der rechte Fuss."""
    # Verschiebe Koordinatensystem, so dass der rechte Fuss dem Ursprung entspricht
    d = np.dot(robot.get_r_foot_endpoint().get_chain_matrix(inverse=True), np.dot(robot.get_l_foot_endpoint().get_chain_matrix(), v.trans3d(z=0.052)))
    d = np.dot(d, v.orig)
    return v.distance(d[:3], dest)

def kick_l_foot_validate(robot):
    """Gibt an, ob die momentane Pose des uebergebenen Roboters auch in der
    Realitaet umgesetzt werden kann. Momentan wird lediglich sicher gestellt,
    dass sich der Schussfuss ueberhalb des Bodens befindet."""
    # Verschiebe Koordinatensystem, so dass der rechte Fuss dem Ursprung entspricht
    p1 = np.dot(robot.get_r_foot_endpoint().get_chain_matrix(inverse=True), np.dot(robot.get_l_foot_endpoint().get_chain_matrix(), v.trans3d(x=0.044,z=0.052)))
    p1 = np.dot(p1, v.orig)
    p2 = np.dot(robot.get_r_foot_endpoint().get_chain_matrix(inverse=True), np.dot(robot.get_l_foot_endpoint().get_chain_matrix(), v.trans3d(x=-0.022,z=-0.052)))
    p2 = np.dot(p2, v.orig)
    return p1[1] >= 0 and p2[1] >= 0

def plot(pose, ball_pos = None, png=False, frame=0, phase=0, bezier=None, mass=None, gplot=False):
    """Plottet den Roboter."""

    robot = Robot()
    robot.update(pose)
    inverse = robot.get_l_foot_endpoint().get_chain_matrix(inverse=True)
    ep = np.empty(4)

    with open("plot/pos%i_%i.gp" % (phase,frame), "w") as plotfile:

        for joint in robot.get_l_leg_chain():
            ep[:3] = joint.get_endpoint()
            ep[3] = 1
            p = np.dot(inverse, ep)
            plotfile.write("%f %f %f\n" % tuple(p[:-1]))

        p = np.dot(robot.get_l_foot_endpoint().get_chain_matrix(inverse=True), np.dot(robot.get_l_foot_endpoint().get_chain_matrix(), v.trans3d(z=0.052)))
        p = np.dot(p, v.orig)
        plotfile.write("%f %f %f\n" % tuple(p[:-1]))
        plotfile.write("\n")

        for joint in robot.get_r_leg_chain():
            ep[:3] = joint.get_endpoint()
            ep[3] = 1
            p = np.dot(inverse, ep)
            plotfile.write("%f %f %f\n" % tuple(p[:-1]))

        p = np.dot(robot.get_l_foot_endpoint().get_chain_matrix(inverse=True), np.dot(robot.get_r_foot_endpoint().get_chain_matrix(), v.trans3d(z=0.052)))
        p = np.dot(p, v.orig)
        plotfile.write("%f %f %f\n" % tuple(p[:-1]))
        plotfile.write("\n")

        for joint in robot.get_l_arm_chain():
            ep[:3] = joint.get_endpoint()
            ep[3] = 1
            p = np.dot(inverse, ep)
            plotfile.write("%f %f %f\n" % tuple(p[:-1]))
        plotfile.write("\n")

        for joint in robot.get_r_arm_chain():
            ep[:3] = joint.get_endpoint()
            ep[3] = 1
            p = np.dot(inverse, ep)
            plotfile.write("%f %f %f\n" % tuple(p[:-1]))
        plotfile.write("\n")

        plotfile.write("%f %f %f\n" % tuple((0.044,0,0.052)))
        plotfile.write("%f %f %f\n" % tuple((-0.022,0,0.052)))
        plotfile.write("%f %f %f\n" % tuple((-0.022,0,-0.052)))
        plotfile.write("%f %f %f\n" % tuple((0.044,0,-0.052)))
        plotfile.write("%f %f %f\n" % tuple((0.044,0,0.052)))
        plotfile.write("\n")

    if ball_pos is not None:
        with open("plot/ball.gp", "w") as plotfile:
            plotfile.write("%f %f %f\n" % tuple(ball_pos))
    else:
        open("plot/ball.gp","w") # remove old data

    if mass is not None:
        with open("plot/mass%i_%i.gp" % (phase, frame), "w") as plotfile:
            ep[:3] = mass
            ep[3] = 1
            mass = np.dot(inverse, ep)
            plotfile.write("%f %f %f\n" % (mass[0], mass[1], mass[2]))
            plotfile.write("%f %f %f\n" % (mass[0], 0, mass[2]))
    else:
        open("plot/mass%i_%i.gp" % (phase, frame),"w") # remove old data

    if bezier is not None:
        bezier.visualize(100, only_data=True, phase=phase)
    else:
        open("plot/bezier_curve%i.gp" % phase,"w") # remove old data

    if gplot:
        g = Gnuplot.Gnuplot(debug=1)
        if png:
            g('set terminal png')
            g('set output "plot/output/kick%i_%i.png"' % (phase,frame))
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
        g('splot "plot/pos%i_%i.gp" every :::0::0 with lines, "plot/pos%i_%i.gp" every :::1::1 with lines, "plot/pos%i_%i.gp" every :::2::2 with lines, "plot/pos%i_%i.gp" every :::3::3 with lines, "plot/pos%i_%i.gp" every :::4::4 with lines, "plot/ball.gp", "plot/bezier_curve%i.gp" with lines, "plot/mass%i_%i.gp"' % (phase, frame, phase, frame, phase, frame, phase, frame, phase, frame, phase, phase, frame))


if __name__ == '__main__':
    run()
