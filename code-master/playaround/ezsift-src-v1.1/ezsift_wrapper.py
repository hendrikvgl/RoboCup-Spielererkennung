import pybridge


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class EZSiftMatchResult():

    def __init__(self):
        self.matching_size_map = {}
        self.matching_coord_map = {}

    def add_result_element(self, reference_key, match_size, match_coord_lst):
        self.matching_coord_map[reference_key] = match_coord_lst
        self.matching_size_map[reference_key] = match_size

    def get_num_reference_keys(self):
        return len(self.matching_size_map.keys())

    def get_match_size(self, reference_key):
        return self.matching_size_map.get(reference_key, 0)

    def get_match_coord_lst(self, reference_key):
        return self.matching_coord_map.get(reference_key, [])

    def __repr__(self):
        return self.matching_size_map.__str__()

    @staticmethod
    def build_from(matching_result_lst):
        formatted_matching_result = [[e[0], e[1], list(chunks(e[2:], 4))] for e in matching_result_lst]
        matching_result = EZSiftMatchResult()
        [matching_result.add_result_element(element[0], element[1], element[2]) for element in formatted_matching_result]
        return  matching_result

class EZSiftImageMatcher():

    def __init__(self):
        self.cpp_ezsift = pybridge.ImageMatcher()

    @staticmethod
    def convert_to_list(image_grey_scale_matrix):
        return [int(item) for sublist in image_grey_scale_matrix for item in sublist]

    def add_reference_image(self, key, image_data_numpy_matrix):
        """ This method adds a reference image to the image matcher
        :param key: A natural language key to reference the image
        :param image_data: The image data of a grey scale image in a matrix form
        """
        grey_scale_image_as_list = EZSiftImageMatcher.convert_to_list(image_data_numpy_matrix)
        img_height, img_width = image_data_numpy_matrix.shape
        self.cpp_ezsift.add_image(key, grey_scale_image_as_list, img_width, img_height)

    def match(self, numpy_image_to_analyze):
        """ This method takes a grey scale numpy image matrix as input and matches that against
            all the images that where added as a reference.
        :param numpy_image_to_analyze: Grey Scale Numpy Image
        :return: EZSiftMatchResult with data about the matching
        """
        #
        img_height, img_width = numpy_image_to_analyze.shape
        image_as_list = EZSiftImageMatcher.convert_to_list(numpy_image_to_analyze)
        matching_result = self.cpp_ezsift.match_with_all(image_as_list, img_width, img_height)

        return EZSiftMatchResult.build_from(matching_result)

    def get_reference_image_confusion_matrix(self):
        """ This method will calculate the matching of the key points between all reference images to
            see if there is any similarity overlapping within the key points """
        return self.cpp_ezsift.get_keypoint_confusion()

    def get_registered_reference_images(self):
        """ This method returns the reference keys for the images which are in the C++ Class,
            together with the number of key points that where calculated for the particular image"""
        reg_lst = self.cpp_ezsift.get_images()
        return list(chunks(reg_lst, 2))
