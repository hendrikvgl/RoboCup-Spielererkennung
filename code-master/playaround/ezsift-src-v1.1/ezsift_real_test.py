import os
import unittest
import numpy as np
import math
import cv2
from ezsift_wrapper import EZSiftImageMatcher


class EZSiftRealImageMatcherTest(unittest.TestCase):

    def test_list_flattening(self):
        ezsift_matcher = EZSiftImageMatcher()

        logo_1 = "example.png"
        image = cv2.imread(os.path.abspath(logo_1))
        grey_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grey_scale_image_1 = np.array(grey_scale_image)
        ezsift_matcher.add_reference_image(logo_1, grey_scale_image_1)

        logo_2 = "logo2.png"
        image = cv2.imread(os.path.abspath(logo_2))
        grey_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grey_scale_image_2 = np.array(grey_scale_image)
        ezsift_matcher.add_reference_image(logo_2, grey_scale_image_2)

        real_photo = "index.png"
        image = cv2.imread(os.path.abspath(real_photo))
        grey_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grey_scale_image_3 = np.array(grey_scale_image)


        print ezsift_matcher.match(grey_scale_image_3)