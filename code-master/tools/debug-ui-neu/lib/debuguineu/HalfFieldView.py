#-*- coding:utf-8 -*-
"""
HalfFieldView
^^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 5/9/14: Created (sheepy)

"""
import cv2
import numpy as np

from debuguineu.VisionView import VisionView


class HalfFieldView(VisionView):

    def __init__(self, data_callback, view_calback):
        super(HalfFieldView, self).__init__(data_callback, view_calback, "Half Field View")
        #self.make_callbacks("glados")
        self.objectdict = {}
        self.buffer_length = 20
        self.center = 305, 410

    def make_callbacks(self, robot):
        self.make_list_callback(robot, "PositionAveraged.x", "PositionAveraged.x")
        self.make_list_callback(robot, "PositionAveraged.y", "PositionAveraged.y")

    def make_list_callback(self, robot, income, outcome):
        self.data_callback(
            "%s::Module.LocalWorldModel.%s" % (robot, income),
            lambda item: self.set_info_list(robot, outcome, item.value/10.0)
        )

    def set_info_list(self, robot, key, value):
        print "HalfFieldView"
        if not robot in self.objectdict:
            self.objectdict[robot] = {}
        if not key in self.objectdict[robot]:
            self.objectdict[robot][key] = []
        self.objectdict[robot][key].append(value)
        if len(self.objectdict[robot][key]) > self.buffer_length:
            self.objectdict[robot][key] = self.objectdict[robot][key][1:]
        self.draw(robot)

    def draw_field_circles(self):
        img = np.zeros((420, 620, 4), np.uint8)
        cv2.line(
            img,
            (110, 110),
            (510, 110),
            (255, 255, 255),
            3)
        cv2.line(
            img,
            (110, 110),
            (110, 410),
            (255, 255, 255),
            3)
        cv2.line(
            img,
            (510, 110),
            (510, 410),
            (255, 255, 255),
            3)
        cv2.line(
            img,
            (110, 410),
            (510, 410),
            (255, 255, 255),
            3)
        cv2.circle(
            img,
            (305, 410),
            60,
            (255, 255, 255),
            3)
        return img

    def draw(self, robot):
        img = self.draw_field_circles()
        self.plot_ball_on_field(img, robot)

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_min = cv2.resize(img, (0, 0), fx=self.FACTOR2, fy=self.FACTOR2)
        #rgbimage = cv2.cvtColor(img,cv2.cv.CV_BGR2RGB)
        #print "Call draw"
        self.show_image(img_min, img, robot)

    def plot_ball_on_field(self, img, robot):
        xl = self.objectdict[robot].get("PositionAveraged.x", [])
        yl = self.objectdict[robot].get("PositionAveraged.y", [])

        assert len(xl) == len(yl)

        for i in range(len(xl)):
            x = xl[i] + self.center[0]
            y = -yl[i] + self.center[1]

            print x, y
            cv2.circle(
            img,
            (int(x), int(y)),
            2,
                (255, 0, 0),
            3)