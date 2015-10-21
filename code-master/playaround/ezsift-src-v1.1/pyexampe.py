from PIL import Image
from PIL import ImageDraw
import os
import itertools
from scipy import misc

__author__ = 'sheepy'

from ezsift_wrapper import EZSiftImageMatcher
import scipy.misc
from fileimagegrabber import ImageFromFileGrabber

color_cycle = itertools.cycle([[255,0,0], [0, 255, 0]])


video_grabber = ImageFromFileGrabber(os.path.abspath("data/"))


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




while True:
    gray, color = video_grabber.grab_frame_return_grey()
    gray = scipy.misc.imresize(gray, 1.0)    #grey_scale_image = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    #grey_scale_image = np.array(grey_scale_image)

    matching_result = ezsift_matcher.match(gray)

    coords_1 = matching_result.get_match_coord_lst(logo_1)
    coords_2 = matching_result.get_match_coord_lst(logo_2)

    print coords_1
    print coords_2

    img = Image.fromarray(color)
    draw = ImageDraw.Draw(img)
    c = color_cycle.next()
    for e in coords_1:
        draw.rectangle((e[2]-2, e[3]-2, e[2]+2, e[3]+2), fill=(255, 0, 0))

    for e in coords_2:
        draw.rectangle((e[2]-2, e[3]-2, e[2]+2, e[3]+2), fill=(0, 255, 0))


    plt.imshow(img)
    plt.show()
