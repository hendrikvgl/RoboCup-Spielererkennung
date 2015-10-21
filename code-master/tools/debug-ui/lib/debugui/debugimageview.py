# -*-coding:utf-8 -*-
from abstractimageview import AbstractImageView
import cv2


class DebugImageView(AbstractImageView):
    FACTOR = 5  # scale for shapes

    def __init__(self, destroy):
        super(DebugImageView, self).__init__(destroy)

    def register_observers(self, name, register):
        self.name = name
        cv2.namedWindow(name, cv2.cv.CV_WINDOW_NORMAL)
        register(name, lambda item: setattr(self, "last_image", item.value))
        register(name + ".Shapes", lambda item: setattr(self,
                 "last_shapes", item.value))
        register(name + ".Draw", lambda item: self.draw())
        register(name + ".Shapes_Locator", lambda item: setattr(
            self, "last_shapes_locator", item.value))
        register(name + ".Draw_Locarot", lambda item: self.draw())
