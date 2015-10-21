import itertools
import cv2
import time

__author__ = 'sheepy'

from ezsift_wrapper import EZSiftImageMatcher
import numpy as np
from videograbber import VideoGrabber

color_cycle = itertools.cycle([[255,0,0], [0, 255, 0], [0, 255, 0]])

"""
#video_grabber = ImageFromFileGrabber(os.path.abspath("data/"))


ezsift_matcher = EZSiftImageMatcher()


logo_1 = "left.png"
image = misc.imread(logo_1, flatten=True) #cv2.imread(os.path.abspath(logo_1))
import matplotlib.pyplot as plt
#grey_scale_image1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#grey_scale_image1 = np.array(grey_scale_image1)
ezsift_matcher.add_reference_image(logo_1, image)

logo_2 = "feld.png"
image = misc.imread(logo_2, flatten=True) #cv2.imread(os.path.abspath(logo_2))
#grey_scale_image2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#grey_scale_image2 = np.array(grey_scale_image2)
ezsift_matcher.add_reference_image(logo_2, image)
"""


ezsift_matcher = EZSiftImageMatcher()

# ML Capture Part:

vidgrab = VideoGrabber(1)


angles_to_capture = [90, 45, 0, -45, -90]
current = 0

cap = True
while cap:

    gray = vidgrab.grab_frame_return_grey()
    grey_scale_image = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    grey_scale_image = np.array(grey_scale_image)

    cv2.imshow('frame', grey_scale_image)

    k = cv2.waitKey(33) & 0xFF
    if k == 27:    # Esc key to stop
        break
    elif k == -1:  # normally -1 returned,so don't print it
        continue
    elif k == ord('c'):
        ezsift_matcher.add_reference_image(str(angles_to_capture[current]), grey_scale_image)
        print "Reference Added", angles_to_capture[current]
        current += 1
        if current >= len(angles_to_capture):
            cap = False
        time.sleep(0.1)


for row in ezsift_matcher.get_reference_image_confusion_matrix():
    print row

while True:

    gray = vidgrab.grab_frame_return_grey()
    grey_scale_image = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    grey_scale_image = np.array(grey_scale_image)

    matching_result = ezsift_matcher.match(grey_scale_image)

    angle = []
    angle_average = 0
    lensall = 0
    for logo_key in angles_to_capture:
        coords_1 = matching_result.get_match_coord_lst(str(logo_key))
        c = color_cycle.next()
        angle_average += int(logo_key) * len(coords_1)
        lensall += len(coords_1)
        angle.append([int(logo_key), len(coords_1)])
        [cv2.circle(gray, (e[2], e[3]), 1, c) for e in coords_1]
        [cv2.circle(gray, (e[2], e[3]), 2, c) for e in coords_1]
        [cv2.circle(gray, (e[2], e[3]), 3, c) for e in coords_1]

    if lensall < 10:
        print "ANGLE don't know"
    else:
        print "ANGLE:", angle_average / float(lensall)
        cv2.putText(gray, "Angle " + str(angle_average / float(lensall)), (10, 30), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0))

    cv2.imshow('frame', gray)
    k = cv2.waitKey(33) & 0xFF
    if k == 27:    # Esc key to stop
        break