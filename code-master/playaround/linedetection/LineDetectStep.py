#-*- coding:utf-8 -*-

import math
import numpy as np
import random
import matplotlib.pyplot as plt


class LineDetectStep():

    def __init__(self, points):
        self.points = points
        self.noise_treshold = 5

    def distance(self, p1, p2, p):
        zaehler = abs((p2[1] - p1[1]) * p[0]  - (p2[0] - p1[0]) * p[1] + p2[0] * p1[1] - p2[1] * p1[0])
        nenner = math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)
        return zaehler / float(nenner)

    def calc_by_distant_point(self, max_dist_point, p1, p2):
        alter_richtungsvektor = np.array([p2[0] - p1[0], p2[1] - p1[1]])
        neuer_richtungsvektor = -(p2[1] - p1[1]), (p2[0] - p1[0])
        punktemenge1 = []
        punktemenge2 = []
        # print alter_richtungsvektor
        for p in self.points:
            vorzeichen = alter_richtungsvektor.dot(np.array(p) - np.array(max_dist_point))
            #print vorzeichen
            if (vorzeichen <= 0):
                punktemenge1.append(p)
            else:
                punktemenge2.append(p)
        t = np.linspace(0, 0.51, 100)
        xs = max_dist_point[0] + t * neuer_richtungsvektor[0]
        ys = max_dist_point[1] + t * neuer_richtungsvektor[1]
        plt.plot(xs, ys, 'ms')
        plt.plot(max_dist_point[0], max_dist_point[1], 'bd')
        plt.plot([e[0] for e in punktemenge1], [e[1] for e in punktemenge1], 'yo')
        plt.plot([e[0] for e in punktemenge2], [e[1] for e in punktemenge2], 'bo')
        plt.axis('equal')
        #plt.show()
        return punktemenge1, punktemenge2



    def process(self):
        if len(self.points) < 10:
            return (1, [self.points])

        p1, p2 = self.lls()

        dist = [[e, self.distance(p1,p2,e)] for e in self.points]
        dist = sorted(dist, key= lambda x: -x[1])

        distances = [self.distance(p1,p2,e) for e in self.points]
        s_distances =  sum(distances) / float(len(distances))
        var_distance = sum([(s_distances-e)**2 for e in distances]) / float(len(distances))

        print "Variance: ", var_distance
        if var_distance < self.noise_treshold:
            return (1, [self.points])

        #print dist

        k = 0
        max_dist_point = dist[k][0]
        punktemenge1, punktemenge2 = self.calc_by_distant_point(max_dist_point, p1, p2)

        g = len(punktemenge1) + len(punktemenge2)
        g /= 3.0


        while len(punktemenge1) < g or len(punktemenge2) < g:
            k += 1
            max_dist_point = dist[k][0]
            punktemenge1, punktemenge2 = self.calc_by_distant_point(max_dist_point, p1, p2)

        plt.title("Title")
        plt.clf()

        plt.plot((p1[0], p2[0]), (p1[1], p2[1]), "y.-")
        plt.plot([s[0] for s in punktemenge1], [s[1] for s in punktemenge1], "ro")
        plt.plot([s[0] for s in punktemenge2], [s[1] for s in punktemenge2], "bo")
        #plt.plot([s[0] for s in  self.points], [s[1] for s in self.points], "md")

        plt.ylim([0, 80])
        plt.xlim([0, 300])
        plt.show()


        return (2, [punktemenge1, punktemenge2])
