# -*- coding:utf-8 -*-
from scipy.stats import pearsonr
import math
from KMeans import KMeans
import numpy as np
import matplotlib.pyplot as plt
import scipy.spatial as sp
import itertools

dp_p = [0, 15, 15, 12]

dp_list = list(itertools.permutations(dp_p))

X = []
Y = []
Z = []

def dst(la, lb):
    dst = [abs(la[i] - lb[i]) for i in range(len(la))]
    return sum(dst)


for l in range(0, 500, 10):
    for k in range(0, 500, 10):
        dp_r = [0-(k-250), 15-(l-250), 15+(k-250), 12+(l-250)]
        result = pearsonr(np.array(dp_p), np.array(dp_r))

        print dp_p, dp_r
        distance_matrix_source_data = sp.distance.cdist([(e, 0) for e in dp_r], [(e, 0) for e in dp_p], 'euclidean')


        print "PGLIST", dp_list
        h = [dst(p, dp_r) for p in dp_list]
        print "H", min(h)

        """
        dst = []
        for i in range(4):
            for j in range(4):
                dst.append((0, distance_matrix_source_data[i][j]))

        lb = min([e[1] for e in dst])
        rb = max([e[1] for e in dst])
        km = KMeans(dst, [(0, lb), (0, rb)])
        km.compute()
        c1, c2 = km.get_clusters()[0], km.get_clusters()[1]
        """

        X.append(l)
        Y.append(k)
        Z.append(min(h))


from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

plt.figure(1, )
ax.scatter(xs=X, ys=Y, zs=Z)
plt.show()