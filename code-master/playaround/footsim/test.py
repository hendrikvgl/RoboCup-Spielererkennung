import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def randrange(n, vmin, vmax):
    return (vmax-vmin)*np.random.rand(n) + vmin

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')


class Foot():
	
	def __init__(self):
    
import random
points = [(random.random(), random.random(), random.random()) for i in range(1000)]
points = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1), (1, 1, 1)]

offset_x = 0.25
offset_y = 0.25
height_offset = 1
points += [(0+offset_x, 0+offset_y, 10), (0+offset_x, 1+offset_y, 10), (1+offset_x, 0+offset_y, 10), (1+offset_x, 1+offset_y, 10), 
(0+offset_x, 0+offset_y, 11+height_offset), (0+offset_x, 3+offset_y, 11+height_offset), (3+offset_x, 0+offset_y, 11+height_offset), (3+offset_x, 3+offset_y, 11+height_offset)]

points += [(0.25, 0.25, 1), (0.25, 0.75, 1), (0.75, 0.25, 1), (0.75, 0.75, 1), (0.25, 0.25, 10), (0.25, 0.75, 10), (0.75, 0.25, 10), (0.75, 0.75, 10)]

vtx = []
for i in range(6):
	vtx += [(0+i*4, 1+i*4), (0+i*4, 2+i*4), (3+i*4, 1+i*4), (3+i*4, 2+i*4)]

for i in range(0, 6, 2):
	vtx += [(0+i*4, 4+i*4), (1+i*4, 5+i*4), (2+i*4, 6+i*4), (3+i*4, 7+i*4)]


ax.scatter([e[0] for e in points], [e[1] for e in points], [e[2] for e in points], marker="o")

for elem in vtx:
    x1, y1, z1 = points[elem[0]]
    x2, y2, z2 = points[elem[1]]
    ax.plot([x1, x2], [y1, y2], [z1, z2], c="g", linestyle="-")

#ax.set_aspect('equal')
#ax.auto_scale_xyz([0, 12], [0, 12], [0, 12])


xc = sum(x for (x, y, z) in points) / len(points)
yc = sum(y for (x, y, z) in points) / len(points)
zc = sum(z for (x, y, z) in points) / len(points)


sx = sy = sz = sL = 0
for i in range(len(points)):   # counts from 0 to len(points)-1
    x0, y0, z0 = points[i - 1]     # in Python points[-1] is last element of points
    x1, y1, z1 = points[i]
    L = ((x1 - x0)**2 + (y1 - y0)**2 + (z1 - z0)**2) ** 0.5
    sx += (x0 + x1)/2.0 * L
    sy += (y0 + y1)/2.0 * L
    sz += (z0 + z1)/2.0 * L
    sL += L
xc = sx / sL
yc = sy / sL
zc = sz / sL

print xc, yc, zc

ax.scatter(xc, yc, zc, c="r", marker="o")

ax.plot([xc, xc], [yc, yc], [zc, -1], c="r", linestyle="-")


import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

point  = np.array([0, 0, 0])
normal = np.array([0, 0, 1])

# a plane is a*x+b*y+c*z+d=0
# [a,b,c] is the normal. Thus, we have to calculate
# d and we're set
d = -point.dot(normal)

# create x,y
xx, yy = np.meshgrid(range(-1, 4), range(-1, 4))

# calculate corresponding z
z = (-normal[0] * xx - normal[1] * yy - d) * 1. /normal[2]

# plot the surface
ax.plot_surface(xx, yy, z)
plt.show()

