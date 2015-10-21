#!/usr/bin/python
import cv2
import numpy
import sys

"""
    Call with at least 3 parameters to see any effect.
    This program creates colormasqs out of a list of "smaller ones"
    The first file is the output file, the remaining are treated as input

    e.g. cumulate_color_masqs masq.png $(find $VIRTUAL_ENV -name "color.png")
"""

def create_united_masq(masqs):
    """
        Loads various masqs and creates a cumulated one
        @masqs list of filenames, the are color masqs

        @return the cumulated masq
    """
    conf = numpy.zeros((256, 768), dtype=numpy.uint8)
    for masq in masqs:
        print "Lade %s" %masq
        colormasq = cv2.imread(masq)[:, :, 0].copy()
        conf[colormasq != 0] = 127


    return conf

def save_color_config(file, config):
    """
        Writes a given color config into a file
        @file the file which will store the new masq
        @config the new color config
    """
    cv2.imwrite(file, config)

args = sys.argv
target = args[1]
masqs = args[2:]

conf = create_united_masq(masqs)
save_color_config(target, conf)
