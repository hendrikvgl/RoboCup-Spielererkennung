#!/usr/bin/env python
#-*- coding:utf-8 -*-
import itertools
import cv2
from sklearn import manifold
from ezsift_wrapper import EZSiftImageMatcher
from embedding_data import StudyImageMDSVisualizer2D
import numpy as np
import matplotlib.pyplot as plt

color_cycle = itertools.cycle([[255,0,0], [0, 255, 0], [0, 255, 0]])

ezsift_matcher = EZSiftImageMatcher()

num_images = 100

for i in range(0, num_images, 1):
    path = "./img/image-{}.png".format(i)
    print path
    img1 = cv2.imread(path)
    g1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    ezsift_matcher.add_reference_image(str(i), g1)


conf_matrix = ezsift_matcher.get_reference_image_confusion_matrix()

np_conf_mat = np.array(conf_matrix)


for i in range(num_images):
    for j in range(num_images):
        if i != j and i > j:
            np_conf_mat[i][j] = np_conf_mat[j][i]

plt.figure(0)
c = plt.imshow(np_conf_mat, interpolation='none')
plt.colorbar(c)


np_conf_mat_inv = np.zeros(np_conf_mat.shape)
for i in range(num_images):
    for j in range(num_images):
            np_conf_mat_inv[i][j] = -1 * np_conf_mat[i][j]

plt.figure(1)
c = plt.imshow(np_conf_mat_inv, interpolation='none')
plt.colorbar(c)

StudyImageMDSVisualizer2D(np_conf_mat_inv).plot()


X_iso = manifold.Isomap(5, n_components=2).fit_transform(np_conf_mat)

C = 10

X_iso = np.array(X_iso)*C
plt.figure(4)
plt.plot([e[0] for e in X_iso], [e[1] for e in X_iso], 'go')
for i in range(len(X_iso)):
    e1, e2 = X_iso[i]
    plt.text(e1, e2, str(i),  fontsize=10)


CX = 100
CY = 100

image_name_list = [cv2.imread("./img/image-{}.png".format(i)) for i in range(len(X_iso))]
list_of_corners = [(e[0]-CX, e[0]+CX*2, e[1]-CY, e[1]+CY*2) for e in X_iso]
for extent, img in zip(list_of_corners, image_name_list):
    plt.imshow(img, extent=extent)

xmin = min([e[0] for e in list_of_corners])
xmax = max([e[1] for e in list_of_corners])

ymin = min([e[2] for e in list_of_corners])
ymax = max([e[3] for e in list_of_corners])

plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)

plt.show()