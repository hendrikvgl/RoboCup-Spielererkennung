import random

__author__ = 'maike'

import os
from readRobotLineData import ReadRobotLineData
import numpy as np
import matplotlib.pyplot as plt
from CircularRegressionHelper import RegressCircLinear


def visualize(_grid):
    x_min = min(_grid.keys())
    print x_min
    x_max = max(_grid.keys())
    print x_max
    y_min = 1000000
    y_max = 0
    for value in _grid.values():
        y_min = min(y_min,min(value))
        y_max = max(y_max, max(value))
    print y_min
    print y_max
    matrix = np.zeros([x_max - x_min, y_max - y_min])

    l = []
    for x in _grid.keys():
        y_values = _grid[x]
        for y in y_values:
            if _grid[x][y] > 0:
                nx, ny = x, y
                if x_min < 0:
                    nx = x + abs(x_min)
                if y_min < 0:
                    ny = y + abs(y_min)
                matrix[nx][ny] = _grid[x][y]
                l.append([nx,ny])

    t, x, y, r = RegressCircLinear(l)
    print x, ",", y, ",", r


    c = plt.imshow(matrix, interpolation="none")
    plt.colorbar(c)

    circle = plt.Circle((y,x),r,color='g', fill=False)
    fig = plt.gcf()
    fig.gca().add_artist(circle)

    plt.show()

def skeletonize(sgrid, sx, sy):
    counter = 0
    if sgrid.get(sx-1, None) is not None:
        if sgrid[sx-1].get(sy+1, 0) > 2:
            counter += 1
    if sgrid.get(sx, None) is not None:
        if sgrid[sx].get(sy+1, 0) > 2:
            counter += 1
    if sgrid.get(sx+1, None) is not None:
        if sgrid[sx+1].get(sy+1, 0) > 2:
            counter += 1
    if sgrid.get(sx-1, None) is not None:
        if sgrid[sx-1].get(sy, 0) > 2:
            counter += 1
    if sgrid.get(sx+1, None) is not None:
        if sgrid[sx+1].get(sy, 0) > 2:
            counter += 1
    if sgrid.get(sx-1, None) is not None:
        if sgrid[sx-1].get(sy-1, 0) > 2:
            counter += 1
    if sgrid.get(sx, None) is not None:
        if sgrid[sx].get(sy-1, 0) > 2:
            counter += 1
    if sgrid.get(sx+1, None) is not None:
        if sgrid[sx+1].get(sy-1, 0) > 2:
            counter += 1
    return counter




rrld = ReadRobotLineData()
points = rrld.get_points(os.path.abspath("embedding_darwin_-{}".format(18)))

grid = {}

for point in points:
    x = int(point[0]/50)
    y = int(point[1]/50)
    if x not in grid:
        grid[x] = {}
    if y not in grid[x]:
        grid[x][y] = 0
    grid[x][y] += 1
    #print grid[x][y]

for x in grid.keys():
    y_values = grid[x]
    for y in y_values:
        if grid[x][y] > 0:
            _counter = skeletonize(grid, x, y)
            if _counter < 1:
                grid[x][y] = -1
           # Hier muss noch bedacht werden, dass die Werte ggf. nicht existieren und neu angelegt werden muessen
           # else:
           #     grid[x-1][y+1] += 1
           #     grid[x][y+1] += 1
           #     grid[x+1][y+1] += 1
           #     grid[x-1][y] += 1
           #     grid[x+1][y] += 1
           #     grid[x-1][y-1] += 1
           #     grid[x][y-1] += 1
           #     grid[x+1][y-1] += 1


visualize(grid)
# Convention: grid[x][y] > 5 is white, else green

exit()


#x = {}

#x[2] = {}

#if eifuegen in x:


#x[2][4] = True

#y = x.get(2, False).get(3, False):

#if 2 in x and 2 in x[2]:

