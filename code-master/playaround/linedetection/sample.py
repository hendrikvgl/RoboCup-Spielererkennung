from KMeans import KMeans
from data import giveit

__author__ = 'sheepy'
import random
import numpy as np
import matplotlib.pyplot as plt
import scipy.spatial as sp

RAND = 4
X = [(i+random.random()*RAND, i+random.random()*RAND) for i in range(100)]
X += [(i+random.random()*RAND, i+random.random()*RAND) for i in range(100)]
X += [(i+random.random()*RAND, i+random.random()*RAND) for i in range(100)]

data, X = giveit()

plt.figure(0)
plt.plot([e[0] for e in X], [e[1] for e in X], 'ro')

k = KMeans(X, [[random.randint(0, 250), random.randint(0, 100)] for e in range(100)])
new_centers = k.compute()

print new_centers
clus = k.get_clusters()
clus = [k for k,v in k.get_clusters().items() if len(v) > 0]

new_centers = np.array(new_centers)[clus]

plt.figure(0)
plt.plot([e[0] for e in new_centers], [e[1] for e in new_centers], 'gd')

new_centers = X

k = 6

distance_matrix_source_data = sp.distance.cdist(new_centers, new_centers, 'euclidean')


for row_idx in range(len(distance_matrix_source_data)):
    row = distance_matrix_source_data[row_idx]
    new_row = [(i, row[i]) for i in range(len(row))]
    sortrow = sorted(new_row, key=lambda e: e[1])
    slicedrow = sortrow[:k]
    idx_rows_knns = [e[0] for e in slicedrow][1:]

    new_row = np.zeros(len(row))
    for idx in idx_rows_knns:
        new_row[idx] = 1

    distance_matrix_source_data[row_idx] = new_row

for i in range(len(distance_matrix_source_data)):
    for j in range(len(distance_matrix_source_data)):
        if distance_matrix_source_data[i][j] == 1:
            p1 = new_centers[i]
            p2 = new_centers[j]
            #plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-')



plt.figure(1)
plt.imshow(distance_matrix_source_data, interpolation='none')

plt.show()
