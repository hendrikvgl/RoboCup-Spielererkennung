.. _ballsuche:

Ballsuche
=========

Basics
------

First of all, all Points matching the Ballcolour, are collected. This happens in the first step of image processing. After that the points
are clustered. Clustering means, putting points together, which are close to in the image. The following steps are the same for all clusters:

Searching the center of gravity of the cluster and calculating the mean distance.
Checking wheather the cluster is alike a circle and collecting boundary points.
If there are enought points, the cluster is validated.
At least we choose the best ball candidate.

Ball Calibration
----------------

The clustering method is so reliable, even the ball color can be calibrate.
Therefore the color masq for the carpet needs to be good. The ball color is calibrated by
processing every cluster under a calculated horizon line which has no carpet color.
First of all the current color masq for the ball will be resettet. Then the ball will be calculated as described above, but using any
point, that doesn't belong to the carpet. Then the color of each point belonging to the ball cluster is added to the resettet ball color
config. An additional threshold is always added to that.
At least the vision can export any color config to a numpy array which can be written into a png file using cv2.
