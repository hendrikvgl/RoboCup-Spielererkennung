import cv2
import numpy as np
import itertools
from mhelper import distance
import matplotlib.pyplot as plt

class CustomHoughTransformation():

    def __init__(self, data, points):
        # computes HoughLines
        self.lines = cv2.HoughLines(data, 0.1, np.pi/360, 10)
        #print lines

        # converts the HoughLines to printable lines in coordinate form
        self.linearray = self.fillLineArrayFromRhoTheta(self.lines, data)

        self.linemapping = self.mapPointsToNearestLine(points, self.linearray)


    def plot_line_assignment(self):
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

    #Takes the HoughLines in rho, theta form, converts them to a coordinate form and saves them to an array
    def fillLineArrayFromRhoTheta(self, inputLines, data):
        #g = np.zeros(data.shape)
        linearray = []
        for rho, theta in inputLines[0]:

            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            linearray.append([x1,y1,x2,y2])
            print rho, theta, [x1,y1,x2,y2]
            cv2.line(data, (x1,y1),(x2,y2),(255, 255, 255), 2)
        return linearray


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
                d = distance((x1,y1),(x2, y2), p)
                dpl.append(d)
                if d < mindist:
                    mindist = d
                    nearestline = l

            print dpl

            if str(nearestline) not in linemapping:
                linemapping[str(nearestline)] = []
            linemapping[str(nearestline)].append(p)
        return linemapping

    def mapLineToEnpoints(self):

        endpointsoflines = []

        for l in self.linearray:
            x1,y1,x2,y2 = l
            endpointsoflines.append((x1,y1))
            endpointsoflines.append((x2,y2))
        return endpointsoflines