# -*- coding:utf-8 -*-
"""
CenterCircleDetection
^^^^^^^^^^^^^^^^^^^^^

This module is an example of how to get a circle from a cloud of points.
There is still some issues with performence which relys on python itself.
All algorithms used are at most n*log(n)

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 20.04.15: Created (sheepy)

"""
import os
import random
import unittest
from scipy.spatial import Delaunay
from collections import defaultdict
from heapq import *
import itertools
import matplotlib.pyplot as plt
import math
import numpy as np
from CircularRegressionHelper import RegressCircLinear, RegressCircNonLinear
from readRobotLineData import ReadRobotLineData
from scipy.sparse.csgraph import dijkstra

COLORS = itertools.cycle(["ro", "bo", "yo", "mo", "go", "co"])

def distance(p1, p2, p):
    zaehler = abs((p2[1] - p1[1]) * p[0]  - (p2[0] - p1[0]) * p[1] + p2[0] * p1[1] - p2[1] * p1[0])
    nenner = math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)
    return zaehler / float(nenner)

def CheckLineThatMustGoThrough(coordinates, x, y, r):
    plt.figure(2)

    coordinates_to_consider = []

    for element in coordinates:
        if CenterCircleMath.distance((x, y), element) < 0.8*r:
            coordinates_to_consider.append(element)

    if len(coordinates_to_consider) == 0:
        return

    g = []
    for angle in range(0, 181, 5):
        rad_angle = math.pi * 2 * (angle / 360.0)

        x1 = math.cos(rad_angle) * r + x
        y1 = math.sin(rad_angle) * r + y
        x2 = math.cos(rad_angle + math.pi) * r + x
        y2 = math.sin(rad_angle + math.pi) * r + y

        plt.plot([x1, x2], [y1, y2], 'r.-')

        average = sum([distance((x1,y1),(x2, y2), p) for p in coordinates_to_consider]) / float(len(coordinates_to_consider))
        g.append((angle, average))

    plt.figure(17)
    plt.plot([rt[0] for rt in g], [rt[1] for rt in g], 'c-', linewidth=4)

    circ = [(math.pi*2*i)/360.0 for i in range(0, 361, 5)]
    xc = [math.cos(e)*r+x for e in circ]
    yc = [math.sin(e)*r+y for e in circ]

    circle_points = zip(xc, yc)

    fullfilled = []

    for dpoint in coordinates:
        nearest_circle_points = [(cp[0], CenterCircleMath.distance(dpoint, (cp[1]))) for cp in zip(range(0, 361, 5), circle_points)]
        nearest_circle_points = sorted(nearest_circle_points, key=lambda x: x[1])
        fullfilled.append(nearest_circle_points[0][0])

    fullfilled = list(set(fullfilled))


    circ = [(math.pi*2*i)/360.0 for i in fullfilled]
    xc = [math.cos(e)*r+x for e in circ]
    yc = [math.sin(e)*r+y for e in circ]

    fk = zip(xc, yc)


    #plt.figure(2)
    #plt.plot([e[0] for e in fk], [e[1] for e in fk], 'gs')

    not_fullfilled = set(range(0, 361, 5)) - set(fullfilled)
    circ = [(math.pi*2*i)/360.0 for i in not_fullfilled]
    xc = [math.cos(e)*r+x for e in circ]
    yc = [math.sin(e)*r+y for e in circ]
    fk = zip(xc, yc)
    #plt.plot([e[0] for e in fk], [e[1] for e in fk], 'rs')


    g = sorted(g, key=lambda h: h[1])

    print g
    plt.figure(3)

    #print g[0:4]
    #g = g[:]

    #a = sum([e[0] for e in g]) / float(len(g))
    a = g[0][0]
    print a
    rad_a = math.pi * 2 * (a / 360.0)

    x1 = math.cos(rad_a) * r + x
    y1 = math.sin(rad_a) * r + y
    x2 = math.cos(rad_a + math.pi) * r + x
    y2 = math.sin(rad_a + math.pi) * r + y

    #plt.plot([e[0] for e in coordinates], [e[1] for e in coordinates], 'go')
    #plt.figure(2)
    #plt.plot([x1, x2], [y1, y2], 'y-', linewidth=5)
    #plt.show()
    return g[0], len(fullfilled), len(not_fullfilled)





class CenterCircleDetection():

    def __init__(self, point_cloud):
        point_cloud = [(int(e[0]), int(e[1])) for e in point_cloud]
        point_cloud = list(set(point_cloud))
        self.point_cloud = point_cloud

    def calculate_minimum_span_tree(self):
        tries = Delaunay(self.point_cloud)

        edges = {}
        nodes = []
        for element in tries.simplices:
            a, b, c = sorted(element)
            nodes.append(a)
            nodes.append(b)
            nodes.append(c)
            p1, p2, p3 = self.point_cloud[a], self.point_cloud[b], self.point_cloud[c]

            if (a, b) not in edges or (b, a) not in edges:
                edges[(a, b)] = int(math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2))
                edges[(b, a)] = int(math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2))

            if (a, c) not in edges or (c, a) not in edges:
                edges[(a, c)] = int(math.sqrt((p1[0] - p3[0])**2 + (p1[1] - p3[1])**2))
                edges[(c, a)] = int(math.sqrt((p1[0] - p3[0])**2 + (p1[1] - p3[1])**2))

            if (b, c) not in edges or (c, b) not in edges:
                edges[(b, c)] = int(math.sqrt((p2[0] - p3[0])**2 + (p2[1] - p3[1])**2))
                edges[(c, b)] = int(math.sqrt((p2[0] - p3[0])**2 + (p2[1] - p3[1])**2))

        edges = [(k[0], k[1], v) for k, v in edges.items()]

        return CenterCircleMath.prim(list(set(nodes)), edges)

    @staticmethod
    def create_adjacency_matrix(size, edges):
        adj_matrix = np.zeros([size, size])

        for edge in edges:
            a, b, dst = edge
            adj_matrix[a][b] = 1
            adj_matrix[b][a] = 1

        return adj_matrix

    def components(self, m):
        d = {}
        used = []
        for i in range(len(m)):
            if i in used:
                continue
            connected = [j for j in range(len(m)) if not math.isinf(m[i][j])]
            d[i] = connected
            for e in connected:
                used.append(e)

        return d

    def find_circles(self, circle_guesses=10, component_splits=100):
        span_tree_edges = self.calculate_minimum_span_tree()
        adjacency_matrix = self.create_adjacency_matrix(len(self.point_cloud), span_tree_edges)
        span_tree_edges = [(-e[2], e[:2]) for e in span_tree_edges]
        heapify(span_tree_edges)

        plt.figure(1)
        result = dijkstra(adjacency_matrix)
        plt.imshow(result, interpolation='none')
        plt.show()

        possible_result_circles = []

        for laufvariable in range(component_splits):

            # Take the longest edge and remove it
            dst, pnt = heappop(span_tree_edges)
            i, j = pnt
            adjacency_matrix[i][j] = 0
            adjacency_matrix[j][i] = 0

            # Calculate the Reachability Matrix with Djikstra (Optimizable)
            # For example with a dict - it is a minimal spanning tree so that should be in O(V)
            result = dijkstra(adjacency_matrix)
            components = self.components(result)
            #plt.figure(1)
            #plt.imshow(result, interpolation='none')

            plt.figure(2)
            for root_point_idx, in_cluster in components.items():
                print "CLUSTER"
                # Consider only components that have more than 10 point
                if len(in_cluster) > 15:
                    # Get the XY Coordinates of the points
                    coordinates = [self.point_cloud[e] for e in in_cluster]
                    coordinates_x = np.array([e[0] for e in coordinates])
                    coordinates_y = np.array([e[1] for e in coordinates])

                    # Plot the cluster with some statistics
                    color = COLORS.next()

                    #plt.plot(coordinates_x, coordinates_y, color)

                    #plt.figure(2)
                    for k1 in in_cluster:
                        for k2 in in_cluster:
                            if adjacency_matrix[k1][k2] > 0:
                                x1, y1 = self.point_cloud[k1]
                                x2, y2 = self.point_cloud[k2]
                                #plt.plot([x1, x2], [y1, y2], color.replace("o", "-"))

                    # Print some statistics for the cluster
                    xmean = coordinates_x.mean()
                    ymean = coordinates_y.mean()

                    # Calculate the distance to the Center Point for every point in the cluster

                    #plt.plot(xmean, ymean, 'mD')
                    #plt.axis('equal')


                    result = RegressCircLinear(coordinates)
                    t, x, y, r = result

                    if r > 3000:
                        continue
                    print t
                    circ = [(math.pi*2*i)/360.0 for i in range(360)]
                    xc = [math.cos(e)*r+x for e in circ]
                    yc = [math.sin(e)*r+y for e in circ]
                    #plt.plot(xc, yc, 'c-', linewidth=4)
                    #plt.plot(x, y, 'cx')

                    try:

                        result = RegressCircNonLinear(coordinates, x, y, r)
                        t, x, y, r, A, B, C = result
                        print t
                        circ = [(math.pi*2*i)/360.0 for i in range(360)]
                        xc = [math.cos(e)*r+x for e in circ]
                        yc = [math.sin(e)*r+y for e in circ]
                        #plt.plot(xc, yc, 'c-', linewidth=4)


                        result = CheckLineThatMustGoThrough(coordinates, x, y, r)

                        if result is None:
                            continue

                        best_angle, fullfilled, not_fullfilled = result

                        error = sum([math.sqrt((r - CenterCircleMath.distance((x,y), e))**2) for e in coordinates]) / float(len(coordinates))
                        #plt.text(x, y,"{}\n{}\n{}\n Error: {}\nREgLineFitErr:{}".format(str(A), str(B), str(C), error, str(best_angle[0])))
                        #plt.plot(x, y, 'cx')

                        #if fullfilled / (fullfilled + not_fullfilled) < 0.5:
                        #    continue
                        c1 = (x, y, r, fullfilled, not_fullfilled, best_angle)
                        print c1
                        possible_result_circles.append(c1)
                    except:
                        pass   


        plt.figure(16)
        plt.plot([e[0] for e in self.point_cloud], [e[1] for e in self.point_cloud], 'go')

        # Needs threshold for
        print "poss", possible_result_circles
        possible_result_circles = [e for e in possible_result_circles if e[3] > 50]
        print "After filter", possible_result_circles

        possible_result_circles = [(int(e[0]), int(e[1]), int(e[2]), int(e[3])) for e in possible_result_circles]
        possible_result_circles = list(set(possible_result_circles))

        for circle11 in possible_result_circles:
            print "Circlce to Draw", circle11
            x = circle11[0]
            y = circle11[1]
            r = circle11[2]
            circ = [(math.pi*2*i)/360.0 for i in range(360)]
            xc = [math.cos(e)*r+x for e in circ]
            yc = [math.sin(e)*r+y for e in circ]
            print xc
            print yc
            plt.plot(xc, yc, 'b-')
        print possible_result_circles
        plt.show()


class TestCenterCircleDetection(unittest.TestCase):

    def test_minimum_span_tree_from_point_cloud(self):
        rrld = ReadRobotLineData()
        points = rrld.get_points(os.path.abspath("embedding_darwin_-{}".format(4)))

        points = [(int(e[0]), int(e[1])) for e in points]
        points = list(set(points))

        ccd = CenterCircleDetection(points)
        result = ccd.calculate_minimum_span_tree()

        plt.plot([e[0] for e in points], [e[1] for e in points], 'ro')
        for edge in result:
            x1, y1 = points[edge[0]]
            x2, y2 = points[edge[1]]
            plt.plot([x1, x2], [y1, y2], 'g-')
        plt.show()

    def test_find_circles(self):
        rrld = ReadRobotLineData()
        points = rrld.get_points(os.path.abspath("embedding_darwin_-{}".format(4)))
        points = [(p[0]*100, p[1]*100) for p in points]

        ccd = CenterCircleDetection(points)
        ccd.find_circles()

    def test_regression(self):
        r = 150
        x, y = 200, 100
        circ = [(math.pi*2*i)/360.0 for i in range(360)]
        xc = [math.cos(e)*r+x + random.randint(1, 40) for e in circ]
        yc = [math.sin(e)*r+y + random.randint(1, 40) for e in circ]
        points = zip(xc, yc)

        f = lambda x: 2*x + 23 + random.randint(1, 3)

        #points += [(i, f(i)) for i in range(150, 300)]

        r = 150
        x, y = 800, 300
        circ = [(math.pi*2*i)/360.0 for i in range(360)]
        xc = [math.cos(e)*r+x+ random.randint(1, 40) for e in circ]
        yc = [math.sin(e)*r+y+ random.randint(1, 40) for e in circ]
        points += zip(xc, yc)

        ccd = CenterCircleDetection(points)
        ccd.find_circles()

    def test_rotation_line_fitting(self):

        cords = [(i, i) for i in range(100)]
        x = 50
        y = 50
        CheckLineThatMustGoThrough(cords, x, y, 30)

class CenterCircleMath(object):

    @staticmethod
    def prim(nodes, edges):
        conn = defaultdict(list)
        for n1, n2, c in edges:
            conn[n1].append((c, n1, n2))
            conn[n2].append((c, n2, n1))

        mst = []
        used = {nodes[0]: 1}
        usable_edges = conn[nodes[0]][:]
        heapify(usable_edges)

        while usable_edges:
            cost, n1, n2 = heappop(usable_edges)
            if n2 not in used:
                used[n2] = 1
                mst.append((n1, n2, cost))

                for e in conn[n2]:
                    if e[2] not in used:
                        heappush(usable_edges, e)
        return mst

    @staticmethod
    def distance(p1, p2):
        return math.sqrt((p1[0] - p2[0])**2+(p1[1] - p2[1])**2)

    @staticmethod
    def find_best_radius(coordinates_x, coordinates_y):



        xmax = max(coordinates_x)
        xmin = min(coordinates_x)

        ymax = max(coordinates_y)
        ymin = min(coordinates_y)


class TestCenterCircleMath(unittest.TestCase):

    def test_prim_algorithm(self):
        nodes = [1, 2, 3, 4]
        edges = [
            (1, 2, 1.0),
            (2, 4, 1.0),
            (2, 3, 2.0),
            (3, 4, 1.0),
            (1, 3, 4.0)
        ]

        minimal_spanning_tree = CenterCircleMath.prim(nodes, edges)
        print minimal_spanning_tree
        self.assertTrue((1, 2, 1.0) in minimal_spanning_tree)
        self.assertTrue((2, 4, 1.0) in minimal_spanning_tree)
        self.assertTrue((2, 3, 2.0) not in minimal_spanning_tree)
        self.assertTrue((4, 3, 1.0) in minimal_spanning_tree)
        self.assertTrue((1, 3, 4.0) not in minimal_spanning_tree)
