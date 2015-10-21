# -*- coding: utf-8 -*-
import numpy as np
cimport numpy as np
np.import_array()

# Konstanten
x_axis = 0
y_axis = 1
z_axis = 2
cdef np.ndarray orig():
    return np.array([0,0,0,1], dtype=np.float)
cdef np.ndarray eye():
    return np.eye(4, dtype=np.float)


cdef np.ndarray roll(float angle):
    """Rotiert im dreidimensionalen Raum (in homogenen Koordinaten) um die x-Achse."""
    return np.array([[1,0,0,0],
                    [0,np.cos(angle), -np.sin(angle),0],
                    [0,np.sin(angle), np.cos(angle),0],
                    [0,0,0,1]], dtype=np.float64)

cdef np.ndarray pitch(float angle):
    """Rotiert im dreidimensionalen Raum (in homogenen Koordinaten) um die y-Achse."""
    return np.array([[np.cos(angle),0,np.sin(angle),0],
                    [0,1,0,0],
                    [-np.sin(angle),0, np.cos(angle),0],
                    [0,0,0,1]], dtype=np.float64)

cdef np.ndarray yaw(float angle):
    """Rotiert im dreidimensionalen Raum (in homogenen Koordinaten) um die z-Achse."""
    return np.array([[np.cos(angle),-np.sin(angle),0,0],
                    [np.sin(angle),np.cos(angle),0,0],
                    [0,0,1,0],
                    [0,0,0,1]], dtype=np.float64)

cdef np.ndarray rot(float angle):
    """Rotiert im zweidimensionalen Raum (in homogenen Koordinaten)."""
    m = np.array([[np.cos(angle), -np.sin(angle), 0],
                 [np.sin(angle), np.cos(angle), 0],
                 [0,0,1]], dtype=np.float64)
    return m

cdef np.ndarray rot3d(float angle, int axis):
    """Rotiert im dreidimensionalen Raum (in homogenen Koordinaten) um die angegebene Achse."""
    if axis == x_axis:
        return roll(angle)
    elif axis == y_axis:
        return pitch(angle)
    elif axis == z_axis:
        return yaw(angle)

cdef np.ndarray trans(float l):
    """
    Führt eine Translation im zweidimensionalen Raum (in homogenen Koordinaten)
    entlang der y-Achse durch.
    """
    m = np.array([[1,0,0],
                  [0,1,l],
                  [0,0,1]], dtype=np.float64)
    return m

cdef np.ndarray trans3d(float z=0, float y=0, float x=0):
    """
    Führt eine Translation im dreidimensionalen Raum (in homogenen Koordinaten) durch.
    """
    return np.array([[1,0,0,x],
                     [0,1,0,y],
                     [0,0,1,z],
                     [0,0,0,1]], dtype=np.float64)

cdef np.ndarray position(list joints):
        """Liefert Numpy-Array mit den Koordinaten des Endpunktes der Gelenkkette."""
        cdef np.ndarray m = np.array([0,0,0,1], dtype=np.float64)
        # Um die Position des Endpunktes zu bestimmen muss für jedes Gelenk
        # eine Translation entsprechend der Länge gefolgt von einer Rotation
        # um den Gelenkwinkel durchgeführt werden.
        for joint in reversed(joints):
            m = trans3d(joint.length) * m
            m = rot3d(joint.angle, joint.axis) * m
        return m

cdef float distance(np.ndarray p1, np.ndarray p2):
    """Liefert den euklidischen Abstand."""
    return  np.linalg.norm(p2-p1)

cdef np.ndarray homogen(np.ndarray v):
    """Normalisiert den Vektor auf die Länge 1."""
    return np.concatenate((v,[1]))
