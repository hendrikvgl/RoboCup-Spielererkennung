# -*-coding:utf-8 -*-
from abstractimageview import AbstractImageView
import cv2
FACTOR = 5


class FieldImageView(AbstractImageView):
    FACTOR = 5  # scale for shapes

    def __init__(self, destroy):
        super(FieldImageView, self).__init__(destroy)

        #cv2.LoadImage('filename')
        mat = cv2.CreateMat(800, 600, cv2.CV_8UC3)
        self.last_image = mat

    def register_observers(self, name, register):
        self.name = name
        cv2.namedWindow(name, cv2.CV_WINDOW_NORMAL)
        self.last_image = cv2.CreateImage((800, 600), cv2.IPL_DEPTH_8U, 3)
        register(name, lambda item: self.process_shapes(item.value))
        register(name + ".DrawDebugShapes", lambda item: self.draw())

    def draw(self):
        """draw new image whenever one arrives
        """
        print "Drawing Image!"
        mat = cv2.CreateMat(800, 600, cv2.CV_8UC3)
        cv2.Set(mat, cv2.RGB(0, 150, 0))
        #Hack to check if the window was closed:
        try:
            cv2.GetWindowProperty(self.name, 0)
        except Exception as e:
            print "Destroying DebugImageView: %s" % e
            self.destroy()
            return
        # Now we draw the debug-shapes
        if self.last_shapes is not None:
            self.draw_debug_shapes(mat, self.last_shapes)
        # Now we draw the locator debug-shapes
        if self.last_shapes_locator is not None:
            self.draw_debug_shapes(mat, self.last_shapes_locator)
        # When that is done all that is left is show the image
        cv2.ShowImage(self.name, mat)

    def process_shapes(self, shapes):
        self.draw()
        new_shapes = []
        robots = []
        for stype, values in shapes:
            if stype == "robot":
                robots.append((stype, values))
            else:
                new_shapes.append((stype, values))

        shapes = new_shapes

        for stype, values in robots:
            self.last_shapes.append(("circle",
                                     {
                                     'x': values['x'] * 100 + 300,
                                     'y': values['y'] * 100 + 400,
                                     'radius': 10,
                                     'color.b': 0,
                                     'color.g': 0,
                                     'color.r': 1}))
        for shape, values in shapes:
            pass
