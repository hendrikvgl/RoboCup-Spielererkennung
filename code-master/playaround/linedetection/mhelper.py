import math
import numpy as np
import random
import matplotlib.pyplot as plt


def lls(points):
    lbound = min([e[0] for e in points])
    rbound = max([e[0] for e in points])

    #points = [(e[1], e[0]) for e in points]

    meanx = sum([e[0] for e in points]) / float(len(points))
    meany = sum([e[1] for e in points]) / float(len(points))
    nenner = 0
    zaehler = 0
    for p in points:
        zaehler += ((p[0] - meanx) * (p[1] - meany))
        nenner += (p[0] - meanx)**2
    m = zaehler / float(nenner)
    p = meany - (m * meanx)


    #lbound = random.randint(0, 100)
    #rbound = random.randint(0, 100)
    p1 = lbound, lbound*m + p #(lbound - p) / m
    p2 = rbound, rbound*m + p #(rbound - p) / m
    return p1, p2, (meanx, meany)

"""
plt.figure(0)
points_example_a = [(i, random.random()) for i in range(100)]
a, b, m = lls(points_example_a)
plt.plot([s[0] for s in points_example_a], [s[1] for s in points_example_a], "ro")
plt.plot([a[0], b[0]], [a[1], b[1]], "y-")
plt.plot(m, "ms")
plt.axis('equal')


plt.figure(1)
points_example_a = [(random.random(), i) for i in range(100)]
a, b, m = lls(points_example_a)

dx = b[0] - a[0]
dy = b[1] - a[1]

anx = a[0] + dx * 10
any = a[1] + dy * 10

bnx = a[0] + dx * -10
bny = a[1] + dy * -10

a = (anx, any)
b = (bnx, bny)

plt.plot([s[0] for s in points_example_a], [s[1] for s in points_example_a], "yo")
plt.plot([a[0], b[0]], [a[1], b[1]], "r-", linewidth=2)
plt.plot(m[0], m[1], "ms")
plt.axis('equal')



from numpy import arange,array,ones#,random,linalg
from pylab import plot,show
from scipy import stats

X = [e[0] for e in points_example_a]
Y = [e[1] for e in points_example_a]

xi = np.array(X)
A = array([ xi, ones(9)])
# linearly generated sequence
y = Y #[19, 20, 20.5, 21.5, 22, 23, 23, 25.5, 24]

slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)

print 'r value', r_value
print  'p_value', p_value
print 'standard deviation', std_err


line = intercept*xi+slope
plt.figure(2)
plt.plot(xi,y,'o', xi,line,'r-')
plt.axis('equal')

points_example_a = [(i, random.random()) for i in range(100)]
X = [e[0] for e in points_example_a]
Y = [e[1] for e in points_example_a]

xi = np.array(X)
A = array([ xi, ones(9)])
# linearly generated sequence
y = Y #[19, 20, 20.5, 21.5, 22, 23, 23, 25.5, 24]

slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)

print 'r value', r_value
print 'p_value', p_value
print 'standard deviation', std_err


line =intercept*xi+slope
plt.plot(xi,y,'o', xi,line,'r-')
plt.axis('equal')
plt.show()
"""
def distance(p1, p2, p):
    zaehler = abs((p2[1] - p1[1]) * p[0]  - (p2[0] - p1[0]) * p[1] + p2[0] * p1[1] - p2[1] * p1[0])
    nenner = math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)
    return zaehler / float(nenner)

from numpy import where, dstack, diff, meshgrid

def find_intersections(A, B):

    # min, max and all for arrays
    amin = lambda x1, x2: where(x1<x2, x1, x2)
    amax = lambda x1, x2: where(x1>x2, x1, x2)
    aall = lambda abools: dstack(abools).all(axis=2)
    slope = lambda line: (lambda d: d[:,1]/d[:,0])(diff(line, axis=0))

    x11, x21 = meshgrid(A[:-1, 0], B[:-1, 0])
    x12, x22 = meshgrid(A[1:, 0], B[1:, 0])
    y11, y21 = meshgrid(A[:-1, 1], B[:-1, 1])
    y12, y22 = meshgrid(A[1:, 1], B[1:, 1])

    m1, m2 = meshgrid(slope(A), slope(B))
    m1inv, m2inv = 1/m1, 1/m2

    yi = (m1*(x21-x11-m2inv*y21) + y11)/(1 - m1*m2inv)
    xi = (yi - y21)*m2inv + x21

    xconds = (amin(x11, x12) < xi, xi <= amax(x11, x12),
              amin(x21, x22) < xi, xi <= amax(x21, x22) )
    yconds = (amin(y11, y12) < yi, yi <= amax(y11, y12),
              amin(y21, y22) < yi, yi <= amax(y21, y22) )

    return xi[aall(xconds)], yi[aall(yconds)]