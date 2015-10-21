import itertools
from data import giveit
import matplotlib.pyplot as plt

#Clusters the input points using kmeans
from CustomHoughProcess import CustomHoughTransformation
from KNNLineRemoval import KMeansDoubleLineRemovalProcess
from readRobotLineData import ReadRobotLineData


rrld = ReadRobotLineData()

points = rrld.get_points("data_darwin/embedding_darwin_-36")
points, data = rrld.get_image(points)
#Receives input data points
#data, points = giveit()

print "Point sTatistics"
print max([e[0] for e in points])
print min([e[0] for e in points])
print max([e[1] for e in points])
print min([e[1] for e in points])

#Plots input data points
plt.figure(1)
plt.imshow(data, interpolation=None)
plt.show()

custom_hough = CustomHoughTransformation(data, points)
custom_hough.plot_line_assignment()
endpointsoflines = custom_hough.mapLineToEnpoints()

plt.figure(1)
plt.imshow(data, interpolation=None)
plt.axis('equal')
plt.show()

kmeans_double_line_removal_process = KMeansDoubleLineRemovalProcess(endpointsoflines, custom_hough.linearray)
groups = kmeans_double_line_removal_process.get_sets_of_points()

single_lines = kmeans_double_line_removal_process.calculate_single_lines()

assignment = CustomHoughTransformation.mapPointsToNearestLine(points, single_lines)

plt.figure(7)
cols = itertools.cycle(["ro", "yo", "go", "mo", "bo", "co"])
for key, values in assignment.items():
    plt.plot([e[0] for e in values],[e[1] for e in values], cols.next())

cols = itertools.cycle(["r-", "y-", "g-", "m-", "b-", "c-"])
for lines in single_lines:
    plt.plot([lines[0], lines[2]], [lines[1], lines[3]], cols.next())
plt.show()