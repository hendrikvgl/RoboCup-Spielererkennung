# -*- coding: utf-8 -*-
import numpy as np
#from bitbots.kick.bezier import Bezier
Bezier=[]

#import Gnuplot


class BezierDurchMergeWiederHierZumVergleichenDerImplementationen(object):
    """Repräsentiert eine Bezier-Kurve."""

    def __init__(self, p0, p1, p2, p3):
        """Konstruktor"""
        # Speichere die Start-, End- und Stützpunkte
        self.p0 = np.array(p0)
        self.p1 = np.array(p1)
        self.p2 = np.array(p2)
        self.p3 = np.array(p3)

        # Speichere Dimension der Punkte
        self.dim = len(p0)

    def posAxis(self, t, axis):
        """Liefert die Position für die angegebene Achse an der Stelle t."""
        if t < 0:
            t = 0
        elif t > 1:
            t = 1
        return (1.0-t)**3 * self.p0[axis] + 3.0 * t * (1.0 - t)**2 * self.p1[axis] + 3.0 * t**2 * (1.0-t) * self.p2[axis] + t**3 * self.p3[axis]

    def pos(self, t):
        """Liefert den Positionsvektor an der Stelle t"""
        p = []
        for i in xrange(self.dim):
            p.append(self.posAxis(t, i))
        return p

    def visualize(self, res, only_data=False, phase=0):
        """Plottet die Bezierkurve."""
        file = open("plot/bezier_curve%i.gp" % phase, "w")
        for t in [x / float(res) for x in xrange(0, res)]:
            x,y,z = self.pos(t)
            file.write("%f %f %f\n" % (x,y,z))
        file.close()

        file = open("plot/bezier_points%i.gp" % phase, "w")
        for i in range(0,3):
            file.write("%f %f %f\n" % tuple(self.p0))
            file.write("%f %f %f\n" % tuple(self.p1))
            file.write("%f %f %f\n" % tuple(self.p2))
            file.write("%f %f %f\n" % tuple(self.p3))
        file.close()

        if not only_data:
            g = Gnuplot.Gnuplot(debug=1)
            g('set terminal wxt persist')
            g('set output "bezier.ps"')
            g('set xlabel "x"')
            g('set ylabel "y"')
            g('set zlabel "z"')
            g('splot "plot/bezier_curve%i.gp" with lines, "plot/bezier_points%i.gp"' % (phase,phase))

if __name__ == '__main__':

    p0 = np.array((1,1,1), dtype=np.float32)
    p1 = np.array((0.5,1.5,1), dtype=np.float32)
    p2 = np.array((-1,0.0,1), dtype=np.float32)
    p3 = np.array((-1.5,1,1), dtype=np.float32)

    bezier = Bezier(p0,p1,p2,p3)
    bezier.visualize(100)
