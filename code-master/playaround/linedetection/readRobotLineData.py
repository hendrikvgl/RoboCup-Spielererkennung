import matplotlib.pyplot as plt
import numpy as np

class ReadRobotLineData():

    # reads in the file and converts it to a points array
    def get_points(self, filename):
        points = []

        with open(filename, 'r') as f:
            for line in f:
                l = line.split(',')
                l[1] = float(l[1].replace('\n',''))
                points.append([float(l[0]), l[1]])

        return points

    # Computes the np image from the points
    def get_image(self, points):
        maxx = max([e[0] for e in points])
        maxy = max([e[1] for e in points])
        print maxy

        minx = min([e[0] for e in points])
        miny = min([e[1] for e in points])

        maxy = (maxy - miny)*100
        maxx = (maxx - minx)*100

        IMG = np.zeros((maxy, maxx),  dtype=np.uint8)

        p = []
        for element in points:
            try:
                x, y = element
                y = (y - miny)*100
                x = (x - minx)*100
                #x, y = int(x), int(y)
                p.append([x, maxy-y])
                IMG[maxy - y][x] = 255
            except:
                pass

        return p, IMG

    # current test data are in 'data_darwin/embedding_darwin_-' and a number between 3 and 162
    # Returns the image and the white points
    def get_data(self, filename):
        p = ReadRobotLineData()
        points = p.get_points(filename)
        IMG = p.get_image(points)
        return IMG, points