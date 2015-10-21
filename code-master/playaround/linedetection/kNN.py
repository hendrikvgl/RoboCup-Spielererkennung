# -*- coding:utf-8 -*-
import random
from scipy.spatial.distance import cdist
from readRobotLineData import ReadRobotLineData
import matplotlib.pyplot as plt

rrld = ReadRobotLineData()

points = rrld.get_points("data_darwin/embedding_darwin_-36")
points, data = rrld.get_image(points)

random.shuffle(points)

plt.figure(1)
plt.plot([e[0] for e in points], [e[1] for e in points], 'go')
plt.axis('equal')


dmatrix = cdist(points, points, 'euclidean')
plt.figure(2)
c = plt.imshow(dmatrix)
plt.colorbar(c)


plt.show()