#-*- coding:utf-8 -*-
"""
DependencyModule
^^^^^^^^^^^^^^^^^^^^

.. moduleauthor:: Robert Schmidt <1schmidt@informatik.uni-hamburg.de>

History:

* 21.11.13: Created (Robert Schmidt)

"""
import gzip
import os
import numpy
from bitbots.modules.abstract import AbstractModule
from bitbots.robot.pypose import PyPose as Pose
#from bitbots.modules.abstract.AbstractModule import debug_m

class DependencyModule(AbstractModule):

    def __init__(self):
        v_env=os.getenv("VIRTUAL_ENV")
        print "Virtual env: %s" %v_env
        if v_env:
            self.image = read_yuyv_file("%s/share/darwin/vision-color-config/testbild.tar.gz" % v_env)
        else:
            self.image = None
        pass

    def start(self,data):
        data["CameraImage"] = None
        data["CameraPose"] = Pose()
        data["CameraFrameVersion"] = -1
        data['CameraResulution'] = (1280,720)
        data['ImageFormat'] = 'YUYV'
        data["CameraExposureCalback"]=None

    def update(self, data):
        #print data["KeyError"]
        data["CameraImage"] = self.image
        if self.image is not None:
            data["CameraFrameVersion"] += 1
        pass


def register(ms):
    ms.add(DependencyModule, "Mock",
           requires=[],
           provides=["CameraResulution", "ImageFormat", "CameraExposureCalback", \
                    "CameraImage", "CameraPose", "CameraFrameVersion"])


def read_yuyv_file(name):
    print "Lese %s" % name
    sizes = (
        (800, 1280 * 2),
        (720, 1280 * 2),
        (480, 640 * 2),
        (600, 800 * 2)
    )

    def estimate_size_for_data(data):
        for height, width in sizes:
            if len(data) == width * height:
                return (height, width)

        raise ValueError("Keine Bildgröße für %d Pixel" % (len(data) / 2))

    oo = gzip.GzipFile if name.endswith(".gz") else open
    with oo(name) as fp:
        data = fp.read()

    size = estimate_size_for_data(data)
    return numpy.fromstring(data, dtype=numpy.uint8).reshape(size)

    return default
