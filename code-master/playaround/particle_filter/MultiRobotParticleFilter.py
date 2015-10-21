# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
from field import get_field
from PFNearestLine import PFNearest
from Particle import FeaturedParticle

field = get_field()

robot_1 = FeaturedParticle(2100, -780, 0)
robot_2 = FeaturedParticle(-2500, -4200, 0)
robot_3 = FeaturedParticle(-2100, 3200, 0)

pfn1 = PFNearest(field, robot_1)
pfn1.algorithm_run()

pfn2 = PFNearest(field, robot_2)
pfn2.algorithm_run()

pfn3 = PFNearest(field, robot_3)
pfn3.algorithm_run()


plt.figure(1)
plt.subplot(311)
xpall = [p.x for p in pfn1.particles]
ypall = [p.y for p in pfn1.particles]
wg = [p.w for p in pfn1.particles]
g = 1.0 / max(wg)
for k in range(len(xpall)):
    col = 1 - g*wg[k]
    plt.plot(xpall[k], ypall[k], color=(col, col, col), marker='o', linestyle='')
plt.ylim([-4700, 4700])
plt.xlim([-3200, 3200])
plt.plot([x[0] for x in field], [x[1] for x in field], 'ro')
plt.plot(robot_1.x, robot_1.y, 'bD')


plt.subplot(312)
xpall = [p.x for p in pfn2.particles]
ypall = [p.y for p in pfn2.particles]
wg = [p.w for p in pfn2.particles]
g = 1.0 / max(wg)
for k in range(len(xpall)):
    col = 1 - g*wg[k]
    plt.plot(xpall[k], ypall[k], color=(col, col, col), marker='o', linestyle='')
plt.ylim([-4700, 4700])
plt.xlim([-3200, 3200])
plt.plot([x[0] for x in field], [x[1] for x in field], 'ro')
plt.plot(robot_2.x, robot_2.y, 'bD')


plt.subplot(313)
xpall = [p.x for p in pfn3.particles]
ypall = [p.y for p in pfn3.particles]
wg = [p.w for p in pfn3.particles]
g = 1.0 / max(wg)
for k in range(len(xpall)):
    col = 1 - g*wg[k]
    plt.plot(xpall[k], ypall[k], color=(col, col, col), marker='o', linestyle='')
plt.ylim([-4700, 4700])
plt.xlim([-3200, 3200])
plt.plot([x[0] for x in field], [x[1] for x in field], 'ro')
plt.plot(robot_3.x, robot_3.y, 'bD')


plt.show()
