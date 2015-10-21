import unittest
import numpy as np
import math
from ezsift_wrapper import EZSiftImageMatcher


class EZSiftImageMatcherTest(unittest.TestCase):

    def test_list_flattening(self):
        list_data = [[1, 2, 3], [2, 2, 5]]
        result = EZSiftImageMatcher.convert_to_list(list_data)
        self.assertEqual(6, len(result))
        self.assertEqual(1, result[0])
        self.assertEqual(2, result[1])
        self.assertEqual(3, result[2])
        self.assertEqual(2, result[3])
        self.assertEqual(2, result[4])
        self.assertEqual(5, result[5])

    def get_test_image(self, param, SQ):
        array = np.array([int(abs(255*math.sin(i/float(param))) * abs(math.cos(255*math.sin(i/10.0)))) for i in range(SQ*SQ)])
        array = array.reshape([SQ, SQ])
        return array



    def test_ez_sift_matching(self):
        SQ = 50
        my_matcher = EZSiftImageMatcher()
        my_matcher.add_reference_image("image_1", self.get_test_image(15.0, SQ))
        my_matcher.add_reference_image("image_2", self.get_test_image(14.0, SQ))
        my_matcher.add_reference_image("image_3", self.get_test_image(15.1, SQ))

        sample_frame = self.get_test_image(15.0, SQ)

        ezsift_matching_result = my_matcher.match(sample_frame)

        self.assertEqual(3, ezsift_matching_result.get_num_reference_keys())
        self.assertEqual(19, ezsift_matching_result.get_match_size("image_1"))
        self.assertEqual(0, ezsift_matching_result.get_match_size("image_2"))
        self.assertEqual(4, ezsift_matching_result.get_match_size("image_3"))

        self.assertEqual(19, len(ezsift_matching_result.get_match_coord_lst("image_1")))
        self.assertEqual(0, len(ezsift_matching_result.get_match_coord_lst("image_2")))
        self.assertEqual(4, len(ezsift_matching_result.get_match_coord_lst("image_3")))

    def test_ezsift_matcher_confusion_matrix(self):
        SQ = 50
        my_matcher = EZSiftImageMatcher()
        my_matcher.add_reference_image("image_1", self.get_test_image(15.0, SQ))
        my_matcher.add_reference_image("image_2", self.get_test_image(14.0, SQ))
        my_matcher.add_reference_image("image_3", self.get_test_image(15.1, SQ))

        ezsift_confusion = my_matcher.get_reference_image_confusion_matrix()
        self.assertEqual([19,  0,  8], ezsift_confusion[0])
        self.assertEqual([ 0, 53,  0], ezsift_confusion[1])
        self.assertEqual([ 4,  0, 20], ezsift_confusion[2])

    def test_ezsift_matcher_registered_images_are_present(self):
        SQ = 50
        my_matcher = EZSiftImageMatcher()
        my_matcher.add_reference_image("image_1", self.get_test_image(15.0, SQ))
        my_matcher.add_reference_image("image_2", self.get_test_image(14.0, SQ))
        my_matcher.add_reference_image("image_3", self.get_test_image(15.1, SQ))

        registered_images = my_matcher.get_registered_reference_images()

        self.assertEqual(['image_1', 30], registered_images[0])
        self.assertEqual(['image_2', 73], registered_images[1])
        self.assertEqual(['image_3', 35], registered_images[2])