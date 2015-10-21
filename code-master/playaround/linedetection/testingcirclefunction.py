from collections import namedtuple
import math
import os
import random
import itertools
import numpy as np
import cmath
import matplotlib.pyplot as plt
from readRobotLineData import ReadRobotLineData


class Circle():

    def __init__(self, xc, yc, r, quality):
        self.xc = xc
        self.yc = yc
        self.r = r
        self.quality = quality

    def __repr__(self):
        return "{}#{}#{}".format(str(self.xc),str(self.yc), str(self.r))

class CircleComputer(object):

    @staticmethod
    def calculate_circle(one, two, three):
        try:
            m_a = (two[1] - one[1]) / (two[0] - one[0])
            m_b = (three[1] - two[1]) / (three[0] - two[0])

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

            return Circle(xc=pos_x, yc=posy, r=radius, quality=-1)
        except Exception as e:
            print e
            return None

    @staticmethod
    def precomputed_circle():
        cpoints = []
        for step in range(360):
            rad_angle = math.pi* 2 * (step / 360.0)
            basic_x = math.cos(rad_angle)
            basic_y = math.sin(rad_angle)
            cpoints.append((basic_x, basic_y))
        return cpoints

    @staticmethod
    def circ_transform(circle):
        pcirc = CircleComputer.precomputed_circle()
        return [(e[0]*circle.r+circle.xc, e[1]*circle.r+circle.yc) for e in pcirc]


class CircleFactory(object):
    """ This class calculates a defined set of circles from
        a point cloud - currently it supports only one circle
    """

    def __init__(self, points):
        self.points = points
        self.num_points = len(points)

    def sample_circles(self, number):
        circles = []
        for k in range(number):
            i = random.randint(0, self.num_points-1)
            j = random.randint(0, self.num_points-1)
            k = random.randint(0, self.num_points-1)

            p1, p2, p3 = self.points[i], self.points[j], self.points[k]

            circle = CircleComputer.calculate_circle(p1, p2, p3)

            if circle is not None:
                circles.append(circle)
        return circles

    def filter_circles_by_radius(self, circles, radius_range):
        assert len(radius_range) == 2
        return [c for c in circles if radius_range[0] < c.r < radius_range[1]]

    def get_test_points(self, num):
        xs = [e[0] for e in self.points]
        ys = [e[1] for e in self.points]
        xmin = min(xs)
        xmax = max(xs)
        ymin = min(ys)
        ymax = max(ys)

        dx = (xmax - xmin) / num
        dy = (ymax - ymin) / num

        f = {}

        for i in range(num):
            lb = xmin + dx*i
            rb = xmin + dx*(i+1)
            for j in range(num):
                tb = ymin + dy*j
                bb = ymin + dy*(j+1)

                if i not in f:
                    f[i] = {}
                if j not in f[i]:
                    f[i][j] = []

                for k in range(len(xs)):
                    xp = xs[k]
                    yp = ys[k]

                    if lb <= xp <= rb and tb <= yp <= bb:
                        f[i][j].append((xp, yp))

        return f


    def dst(self, a, b):
        return math.sqrt( (a[1] - b[1])**2 + (a[0] - b[0])**2)

    def test_circle_quality(self, circles, num_points):
        test_points = []
        """
        f = self.get_test_points(num_points)
        for i in range(num_points):
            for j in range(num_points):
                if len(f[i][j]) > 0:
                    p = random.choice(f[i][j])
                    test_points.append(p)
        """
        random.shuffle(self.points)
        test_points = self.points[:num_points]
        for circle in circles:
            quality_estimation = self.estimate_quality(circle, test_points)
            circle.quality = quality_estimation


    def estimate_quality(self, circle, test_points):

        lst = []
        for pnt in test_points:
            x, y = pnt

            dx, dy = circle.xc - x, circle.yc - y

            polar = cmath.polar(complex(float(dx), float(dy)))
            squared_radius_distance = (self.dst(pnt, (circle.xc, circle.yc)) - circle.r)**2
            lst.append([polar, squared_radius_distance])
        parsed = [360*e[0][1]/(2*math.pi) for e in lst]
        cum_error = sum([e[1] for e in lst])
        f = self.binning_angles(parsed)
        circle.quality = cum_error / f
        return lst

    def binning_angles(self, list_of_angles):
        bins = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for element in list_of_angles:
            element += 180
            bins[int(element / 20)] += 1
        return np.array(bins).var() #max(1, len(bins) - len([e for e in bins if e == 0]))

    def filter_circles_by_polygon_boundaries(self, circles):
        xs = [e[0] for e in self.points]
        ys = [e[1] for e in self.points]
        xmin = min(xs)
        xmax = max(xs)
        ymin = min(ys)
        ymax = max(ys)

        return [c for c in circles if xmin < c.xc < xmax and ymin < c.yc < ymax]



rrld = ReadRobotLineData()
points = rrld.get_points(os.path.abspath("embedding_darwin_-{}".format(16)))




circle_factory = CircleFactory(points)
circles = circle_factory.sample_circles(number=200)
circles = circle_factory.filter_circles_by_radius(circles, [0, 5000])
circles = circle_factory.filter_circles_by_polygon_boundaries(circles)





circle_factory.test_circle_quality(circles, num_points=len(points))


for circle in sorted(circles, key=lambda c: c.quality):
    print circle.xc, circle.yc, circle.r, circle.quality

#plt.plot(range(len(circles)), [e.r for e in circles], "r-")
#plt.plot(range(len(circles)), [e.quality for e in circles], "g-")

plt.figure(2)
plt.plot([e[0] for e in points], [e[1] for e in points], 'go')

for circle in circles[:10]:
    pcirc = CircleComputer.circ_transform(circle)
    plt.plot([e[0] for e in pcirc], [e[1] for e in pcirc], 'r-')
    plt.plot(circle.xc, circle.yc, 'mD')



plt.show()

"""

    potential_circles = []

    for k in range(100):
        random.shuffle(points)
        a, b, c = points[0:3]
        circle = get_circle(a, b, c)

        random.shuffle(points)
        test = points[:5]

        distances = sum([(dst(e, circle[0]) - circle[1])**2 for e in test])

        print distances


        if circle[1] < 10000:
            potential_circles.append([distances, circle])

            pcirc = circ_transform(circle[0], circle[1])
            #plt.plot([e[0] for e in pcirc], [e[1] for e in pcirc], 'r-')

            plt.plot(circle[0][0], circle[0][1], 'mD')


    sorted_cirlces = sorted(potential_circles, key=lambda x: x[0])
    num_circles_to_consider = 10

    for element in sorted_cirlces[:num_circles_to_consider]:
        ds, circle = element

        pcirc = circ_transform(circle[0], circle[1])
        #plt.plot([e[0] for e in pcirc], [e[1] for e in pcirc], 'r-')

        plt.plot(circle[0][0], circle[0][1], 'rD')

    circles_filtered = [e[1] for e in sorted_cirlces[:num_circles_to_consider]]

    xcenters = np.array([e[0][0] for e in circles_filtered])
    ycenters = np.array([e[0][1] for e in circles_filtered])
    radcenters = np.array([e[1] for e in circles_filtered])


    mean_circle = (xcenters.mean(), ycenters.mean()), radcenters.mean()


    plt.plot([e[0] for e in points], [e[1] for e in points], 'gx')


    pcirc = circ_transform(mean_circle[0], mean_circle[1])
    plt.plot([e[0] for e in pcirc], [e[1] for e in pcirc], 'b-')
    plt.plot(mean_circle[0][0], mean_circle[0][1], 'bD')

    plt.show()
except:
    pass
"""