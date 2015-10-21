# -*- coding:utf-8 -*-
from os import listdir
from os.path import isfile, join
from scipy import misc

class ImageFromFileGrabber():

    def __init__(self, device):
        self.file_path = device
        self.onlyfiles = [f for f in listdir(device) if isfile(join(device, f))]
        self.path_generator = self.image_generator()

    def image_generator(self):
        c = 0
        while True:
            yield self.onlyfiles[c]
            c += 1

    def grab_frame_return_grey(self):
        path = self.path_generator.next()
        return misc.imread(join(self.file_path, path), flatten=True), misc.imread(join(self.file_path, path))

