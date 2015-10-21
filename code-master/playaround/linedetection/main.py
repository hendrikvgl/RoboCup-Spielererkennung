import random
import math
from LineDetectStep import LineDetectStep

__author__ = 'sheepy'


import matplotlib.pyplot as plt
import numpy as np


m = [
    (10, 10),
    (150, 10),
    (150, 50),
    (250, 50)
]

step_division = 100
noise = 2
points = []

for i in range(len(m) -1):
    a, b = m[i], m[i+1]

    for k in range(step_division):
        p = k / float(step_division)

        px = a[0]*p + (1-p)*b[0]
        py = a[1]*p + (1-p)*b[1]

        px = random.gauss(px, noise)
        py = random.gauss(py, noise)

        points.append([px, py])

ax = plt.gca()
ax.set_axis_bgcolor('green')
plt.figure(0)
initial_point_maps = [points]

for i in range(10):
    new_line_sets = []
    for element in initial_point_maps:
        l = LineDetectStep(element)
        num, data = l.process()

        if num == 2:
            new_line_sets.append(data[0])
            new_line_sets.append(data[1])
        elif num == 1:
            new_line_sets.append(data[0])
        else:
            print "sadddddddddddddddddd"

    initial_point_maps = new_line_sets






plt.figure(1)
for e in initial_point_maps:
    try:
        plt.plot([s[0] for s in e], [s[1] for s in e], marker='o', color=(random.random(), random.random(), random.random()))
    except Exception as e:
        print "Dont draw", e
        pass
plt.axis('equal')
plt.show()