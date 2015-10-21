# -*- coding: utf-8 -*-
from libcpp cimport bool
import numpy as np
cimport numpy as np
np.import_array()
import Gnuplot


cdef class Bezier(object):
    """Repräsentiert eine Bezier-Kurve."""

    def __cinit__(self, np.ndarray p0, np.ndarray p1, np.ndarray p2, np.ndarray p3):
        """Konstruktor"""
        # Speichere die Start-, End- und Stützpunkte
        self.p0 = np.array(p0)
        self.p1 = np.array(p1)
        self.p2 = np.array(p2)
        self.p3 = np.array(p3)

        # Speichere Dimension der Punkte
        self.dim = len(p0)

    cdef float posAxis(self, float t, int axis):
        """Liefert die Position für die angegebene Achse an der Stelle t."""
        if t < 0:
            t = 0
        elif t > 1:
            t = 1
        return (1.0-t)**3 * self.p0[axis,0] + 3.0 * t * (1.0 - t)**2 * self.p1[axis,0] \
                + 3.0 * t**2 * (1.0-t) * self.p2[axis,0] + t**3 * self.p3[axis]

    cdef list pos(self, float t):
        """Liefert den Positionsvektor an der Stelle t"""
        p = []
        for i in xrange(self.dim):
            p.append(self.posAxis(t, i))
        return p

    cpdef visualize(self, int res, bool only_data=False, int phase=0):
        """Plottet die Bezierkurve."""
        file = open("plot/bezier_curve%i.gp" % phase, "w")
        for t in [x / float(res) for x in xrange(0, res)]:
            x,y,z = self.pos(t)
            file.write("%f %f %f\n" % (x,y,z))
        file.close()

        file = open("plot/bezier_points.gp", "w")
        for i in range(0,3):
            file.write("%f %f %f\n" % (float(self.p0[0,0]), float(self.p0[1,0]), float(self.p0[2,0])))
            file.write("%f %f %f\n" % (float(self.p1[0,0]), float(self.p1[1,0]), float(self.p1[2,0])))
            file.write("%f %f %f\n" % (float(self.p2[0,0]), float(self.p2[1,0]), float(self.p2[2,0])))
            file.write("%f %f %f\n" % (float(self.p3[0]), float(self.p3[1]), float(self.p3[2])))
        file.close()

        if not only_data:
            g = Gnuplot.Gnuplot(debug=1)
            g('set terminal wxt persist')
            g('set output "bezier.ps"')
            g('set xlabel "x"')
            g('set ylabel "y"')
            g('set zlabel "z"')
            g('splot "plot/bezier_curve.gp" with lines, "plot/bezier_points.gp"' )
