import math
import os
import random
import matplotlib.pyplot as plt
from readRobotLineData import ReadRobotLineData
import numpy as np
import scipy.spatial as sp

def precomputed_circle():
    cpoints = []
    for step in range(360):
        rad_angle = math.pi* 2 * (step / 360.0)
        basic_x = math.cos(rad_angle)
        basic_y = math.sin(rad_angle)
        cpoints.append((basic_x, basic_y))
    return cpoints

def circ_transform(center, radius):
    xoff, yoff = center
    pcirc = precomputed_circle()
    return [(e[0]*radius+xoff, e[1]*radius+yoff) for e in pcirc]

def dst(a, b):
    return math.sqrt( (a[1] - b[1])**2 + (a[0] - b[0])**2)

def get_circle(one, two, three):
    m_a = (two[1] - one[1]) /  (two[0] - one[0])
    m_b = (three[1] - two[1]) /  (three[0] - two[0])

    assert one != two and two != three and one != three

    pos_x, posy = 0, 0
    radius = 0

    if m_a != m_b and not math.isinf(m_a) and not math.isinf(m_b) and not math.isnan(m_a) and not math.isnan(m_b):

        pos_x = (m_a * m_b * (three[1] - one[1]) + m_a * (two[0] + three[0]) - m_b * (one[0] + two[0])) / (2 * (m_a - m_b))

        if m_a != 0.0:
            posy = ((float(one[1] + two[1]) / 2) - (pos_x - float(one[0] + two[0]) / 2) / m_a)
        elif m_b != 0.0:
            posy = ((float(two[1] + three[1]) / 2) - (pos_x - float(two[0] + three[0]) / 2) /m_b)

        radius = math.sqrt((one[0] - pos_x)**2 + (one[1] - posy)**2)

    return (pos_x, posy), radius

rrld = ReadRobotLineData()
points = rrld.get_points(os.path.abspath("embedding_darwin_-{}".format(17)))

points = circ_transform((0, 0), 100)
points += [(i, i*10) for i in range(100)]
#points += [(0,0)]
#points += [(0,0)]
#points += [(0,0)]
#points += [(0,0)]
#points += [(0,0)]

random.shuffle(points)

rand_points = points[:len(points)]

lst = []

for i in range(len(rand_points)):
    for j in range(len(rand_points)):
        lst.append((i, j, dst(rand_points[i], rand_points[j])))

lst = sorted(lst, key=lambda x: x[2])

plt.figure(0)
plt.plot(range(len(lst)), [e[2] for e in lst], 'r-')
plt.show()