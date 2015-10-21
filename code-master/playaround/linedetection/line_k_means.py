import math
import itertools
import random
import matplotlib.pyplot as plt
from mhelper import distance
from readRobotLineData import ReadRobotLineData
import numpy as np

class KMeans():

    def __init__(self, points, centers):
        self.points = points
        self.centers = centers
        self.old_centers = None
        self.clusters = None

    def get_clusters(self):
        return self.clusters

    def compute(self):
        self.compute_one_step()
        steps = 1

        while self.centers_still_move():
            steps +=1
            self.compute_one_step()

        return self.centers

    def compute_one_step(self):
        self.clusters = self.compute_cluster_assignments()
        avrg = self.compute_average_in_cluster(self.clusters)
        new_centers = []
        for i in range(len(self.centers)):
            new_centers.append((avrg[i][0], avrg[i][1]))
        self.old_centers = self.centers
        self.centers = new_centers

    def compute_cluster_assignments(self):
        clusters = {i: [] for i in range(len(self.centers))}

        for i in range(len(self.points)):
            p = self.points[i]
            distances = [self.distance(e, p) for e in self.centers]
            minimum_index = distances.index(min(distances))
            clusters[minimum_index].append(p)
        return clusters

    def distance(self, e, p):
        return math.sqrt((e[0] - p[0])**2 + (e[1] - p[1])**2)

    def compute_average_in_cluster(self, clusters):
        avrgs = {}
        for i in clusters.keys():
            c = clusters[i]
            l = len(c)
            if l != 0:
                x_av = sum([e[0] for e in c]) / float(l)
                y_av = sum([e[1] for e in c]) / float(l)
                avrgs[i] = [x_av, y_av]
            else:
                avrgs[i] = (self.centers[i][0], self.centers[i][1])
        return avrgs

    def centers_still_move(self):
        for i in range(len(self.centers)):
            old = self.old_centers[i]
            current = self.centers[i]

            if abs(old[0] - current[0]) > 1E-5 and abs(old[1] - current[1]) > 1E-5:
                return True

    @staticmethod
    def class_distance(p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    # Maps given input points to the nearest given line
    @staticmethod
    def mapPointsToNearestLine(inputPoints, inputLineArray):
        linemapping = {}

        for p in inputPoints:
            mindist = 99999999999999999999999999999999999999999999999
            nearestline = None
            dpl = []
            for l in inputLineArray:
                x1,y1,x2,y2 = l
                xm, ym = (x1 +x2) / 2.0, (y1 + y2) / 2.0
                dx = x1 - xm
                dy = y1 - ym
                dx, dy = -dy, dx

                ort_x1 = xm + dx
                ort_y1 = ym + dy



                d = distance((x1,y1),(x2, y2), p) + distance((xm, ym), (ort_x1, ort_y1), p)
                dpl.append(d)
                if d < mindist:
                    mindist = d
                    nearestline = l

            if str(nearestline) not in linemapping:
                linemapping[str(nearestline)] = []
            linemapping[str(nearestline)].append(p)
        return linemapping

    def plot_line_assignment(self, line_assignment):
        lins = itertools.cycle(["r-", "y-", "g-", "m-", "b-", "c-"])
        cols = itertools.cycle(["ro", "yo", "go", "mo", "bo", "co"])
        for key, values in self.linemapping.items():
            print "K",
            key = eval(key)
            plt.plot([key[0], key[2]], [key[1], key[3]], lins.next())
            plt.plot([e[0] for e in values],[e[1] for e in values], cols.next())
        plt.xlim([0, 200])
        plt.ylim([0, 100])
        plt.show()


rrld = ReadRobotLineData()

points = rrld.get_points("data_darwin/embedding_darwin_-36")
points, data = rrld.get_image(points)
#Receives input data points
#data, points = giveit()


#points = [(x*random.random(), 2*random.random()) for x in range(40)] + [(4*random.random(), y*random.random()) for y in range(80)]


print "Point sTatistics"
xmax = max([e[0] for e in points])
xmin = min([e[0] for e in points])
ymax = max([e[1] for e in points])
ymin = min([e[1] for e in points])

x = [e[0] for e in points]
y = [e[1] for e in points]

basis = np.array(x).mean(), np.array(y).mean()

lines = []

def generate_line(center, angle):
    tpx = np.cos(angle) + center[0]
    tpy = np.sin(angle) + center[1]

    x1 = center[0] + 50 * (center[0] - tpx)
    y1 = center[1] + 50 * (center[1] - tpy)

    x2 = center[0] + -50 * (center[0] - tpx)
    y2 = center[1] + -50 * (center[1] - tpy)

    return [x1, y1, x2, y2]


for i in range(10):
    bas = basis[0] + 20 * (random.random() - 0.5), basis[1] + 20 * (random.random() - 0.5)
    theta = 2*math.pi*random.random()

    line = generate_line(bas, theta)
    lines.append(line)


for rounds in range(100):
    assignment = KMeans.mapPointsToNearestLine(points, lines)
    cols = itertools.cycle(["ro", "yo", "go", "mo", "bo", "co"])

    new_lines = []
    new_centers = []
    for key, values in assignment.items():
        xm = np.array([e[0] for e in values]).mean()
        ym = np.array([e[1] for e in values]).mean()

        new_possible_lines = [generate_line((xm, ym), 2*math.pi*(angle/360.0)) for angle in range(0, 361, 2)]
        lines_with_error = [(sum([distance((_line[0], _line[1]), (_line[2], _line[3]), p) for p in values]), _line) for _line in new_possible_lines]
        lines_with_error_sorted = sorted(lines_with_error, key=lambda fg: fg[0])
        new_lines.append(lines_with_error_sorted[0][1])
        new_centers.append((xm, ym))

    lines = new_lines
    centers = new_centers

    # Calculate the center of the assignment
    # Calculate for each of those centers all lines through that center and recalculate the error
    # Choose the line for the new stuff which minimizes the error - do that for all
    # Repeat

    plt.figure(rounds)

    for line in lines:
        plt.plot([line[0], line[2]], [line[1], line[3]], "g-")
        x1, y1, x2, y2 = line
        xm, ym = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        dx = x1 - xm
        dy = y1 - ym

        dx, dy = -dy, dx

        x1 = xm + dx
        y1 = ym + dy

        plt.plot([xm, x1], [ym, y1], "r-")



    for center in centers:
        plt.plot(center[0], center[1], "gD")

    #plt.plot([e[0] for e in points], [e[1] for e in points], 'ms')

    plt.plot(np.array(x).mean(), np.array(y).mean(), 'yd')

    #for k, values in assignment.items():
        #plt.plot([e[0] for e in values], [e[1] for e in values], cols.next())

    plt.xlim([-20+xmin, 20+xmax])
    plt.ylim([-20+ymin, 20+ymax])
    plt.axis('equal')

    plt.show()
