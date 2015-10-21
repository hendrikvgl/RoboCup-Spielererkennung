#-*- coding:utf-8 -*-
"""
VisionView
^^^^^^^^^^

Implementation of the VisionView, which, opens the ImageView.glade-data and implements all the neccessary methods to
show the information of the robots about what they perceive through their Camera.


:platform: Unix and Windows

.. moduleauthor:: Robocup-AG in cooperation with Projekt-Debug-UI (implemented by Nils Rokita and partly old Code)

.. autoclass:: VisionView(GenericNotebookView)
    :members:

:members:
"""
from genericView import GenericNotebookView

import gtk

from bitbots.util import generate_find, find
import numpy as np
from math import sin, cos

import cv2

try:
    find('share/debug-ui-neu')
    find = generate_find('share/debug-ui-neu')
except:
    find = generate_find('tools/debug-ui-neu/share/debug-ui-neu')


class VisionView(GenericNotebookView):

    FACTOR = 5  # has to be 5, due to downscale on sender side
    FACTOR2 = 0.5  # downscale vor better view

    def __init__(self, data_callback, view_calback, name="Vision View"):
        super(VisionView, self).__init__(name,
                                         data_callback, view_calback)

        self.last_image = None
        self.imageviewdict = {}
        self.imagedict = {}
        self.shapesdict = {}
        self.imagetypedict = {}
        self.imagestepdict = {}
        self.robots = []

    def add_new_robot(self, name):
        self.robots.append(name)
        self.make_callbacks(name)
        """
        view_int = gtk.Viewport()
        image_int = gtk.Image()
        view_ext = gtk.Viewport()
        image_ext = gtk.Image()
        view_int.add(image_int)
        view_ext.add(image_ext)
        view_int = gtk.TreeView()
        view_ext = gtk.TreeView()
        self.add_notebook_page(name, view_int, view_ext)

        """
        builder_int = gtk.Builder()
        builder_int.add_objects_from_file(
            find("VisionView.glade"), ("ImageView",))
        motor_view_int = builder_int.get_object('ImageView')
        builder_ext = gtk.Builder()
        builder_ext.add_objects_from_file(
            find("VisionView.glade"), ("ImageView",))
        motor_view_ext = builder_ext.get_object('ImageView')

        self.add_notebook_page(name, motor_view_int, motor_view_ext)

        self.imageviewdict[name + "_int"] = builder_int.get_object("Image")
        self.imageviewdict[name + "_ext"] = builder_ext.get_object("Image")

        pass

    def make_callbacks(self, robot):
        name = robot + "::Vision.DebugImage"
        self.data_callback(name, lambda item:
                           self.imagedict.__setitem__(robot, item.value))
        self.data_callback(name + ".Shapes", lambda item:
                           self.shapesdict.__setitem__(robot, item.value))
        self.data_callback(name + ".Draw", lambda item: self.draw(robot))
        self.data_callback(name + ".Type", lambda item:
                           self.imagetypedict.__setitem__(robot, item.value))
        self.data_callback(name + ".Factor", lambda item:
                           self.imagestepdict.__setitem__(robot, item.value))

    def show_image(self, img_min, img, robot):
        """
        Converts the Image to GTK and draw it in the Gui
        """
        """img_pixbuf = gtk.gdk.pixbuf_new_from_data(img.imageData,
                                          gtk.gdk.COLORSPACE_RGB,
                                          False,
                                          img.depth,
                                          img.width,
                                          img.height,
                                          img.widthStep)"""
        img_pixbuf = gtk.gdk.pixbuf_new_from_array(
            img, gtk.gdk.COLORSPACE_RGB, 8)
        img_min_pixbuf = gtk.gdk.pixbuf_new_from_array(
            img_min, gtk.gdk.COLORSPACE_RGB, 8)

        self.imageviewdict[robot + "_int"].set_from_pixbuf(img_min_pixbuf)
        self.imageviewdict[robot + "_ext"].set_from_pixbuf(img_pixbuf)

    def draw(self, robot):
        """
        Get Image, resize draw debugshapes, and recolerisize, resize for output
        """
        if self.imagetypedict.get(robot, "bw") == "rgb":
            img = cv2.cvtColor(self.imagedict[robot], cv2.COLOR_RGB2BGR)
        else:
            img = cv2.cvtColor(self.imagedict[robot], cv2.COLOR_GRAY2BGR)
        factor = self.imagestepdict.get(robot, self.FACTOR)
        img = cv2.resize(img, (0, 0), fx=factor, fy=factor)
        draw_debug_shapes(img, self.shapesdict[robot])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_min = cv2.resize(img, (0, 0), fx=self.FACTOR2, fy=self.FACTOR2)
        self.show_image(img_min, img, robot)

    def get_internal_state(self):
        state = {'VisionView.robots': self.robots}
        state.update(super(VisionView, self).get_internal_state())
        return state

    def set_internal_state(self, state):
        super(VisionView, self).set_internal_state(state)
        for robot in state['VisionView.robots']:
            self.add_new_robot(robot)


class FieldView(VisionView):
    def __init__(self, data_callback, view_calback):
        super(FieldView, self).__init__(data_callback, view_calback, "Field View")

    def make_callbacks(self, robot):
        name = robot + "::Locator.Field"
        self.data_callback(name + ".Shapes", lambda item:
                           self.shapesdict.__setitem__(robot, item.value))
        self.data_callback(name + ".Draw", lambda item: self.draw(robot))

    def draw(self, robot):
        """
        Get Image, resize draw debugshapes, and recolerisize, resize for output
        """
        img = np.zeros((300, 400, 3), np.uint8)
        lines = [(
            (-3, 2), (3, 2)), ((-3, -2), (3, -2)), ((-3, 1.1), (-2.4, 1.1)),
            ((2.4, 1.1), (3, 1.1)), ((-3, -1.1), (-2.4, -1.1)
                                     ), ((2.4, -1.1), (3, -1.1)),
            ((-3, -2), (3, -2)), ((-3, -2), (-3, 2)), ((-2.4, -
                                                        1.1), (-2.4, 1.1)),
            ((0, -2), (0, 2)), ((2.4, -1.1), (2.4, 1.1)), ((3, -2), (3, 2))]
        for ((x1, y1), (x2, y2)) in lines:
            if x1 < x2:
                for idx in range(int(50 * (x1 + 4)), int(50 * (x2 + 4))):
                    y = 50 * (y1 + 3)
                    img[y][idx] = (255, 255, 255)
            else:
                for idy in range(int(50 * (y1 + 3)), int(50 * (y2 + 3))):
                    x = 50 * (x1 + 4)
                    img[idy][x] = (255, 255, 255)
        cv2.circle(
            img, (int(50 * 4), int(50 * 3)), int(50 * 0.6), (255, 255, 255))
        shapes = self.shapesdict[robot]

        draw_debug_shapes(img, shapes, True)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_min = cv2.resize(img, (0, 0), fx=self.FACTOR2, fy=self.FACTOR2)
        #rgbimage = cv2.cvtColor(img,cv2.cv.CV_BGR2RGB)
        self.show_image(img_min, img, robot)





def draw_debug_shapes(mat, shapes, field=False):
    """Draw set of debug shapes on the image mat
    """
    for shape in shapes:
        stype, values = shape
        if not all(v == v for v in values.values()):
            # filter out NaN
            continue

        if field:
            for key in values:
                if key in ('x', 'x1', 'x2'):
                    values[key] += 4
                    values[key] *= 50
                if key in ('y', 'y1', 'y2'):
                    values[key] = - values[key] + 3
                    values[key] *= 50
                if key in ('radius'):
                    values[key] *= 50
                if key in ('rot'):
                    pass
                    #values[key] *= 180/pi
                # 400x300 bild

        def description():
            """Puts description text of this item in the picture
            """
            if not values.get("text", ""):
                return
                cv2.putText(
                    mat,
                    values["text"],
                    (int(values["x"] + 3), int(values["y"] + 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (int(values["color.b"] * 255),
                        int(values["color.g"] * 255),
                        int(values["color.r"] * 255)))

        if stype == "line":
            try:
                cv2.line(
                    mat,
                        (int(values["x1"]), int(values["y1"])),
                        (int(values["x2"]), int(values["y2"])),
                        (int(values["color.b"] * 255),
                         int(values["color.g"] * 255),
                         int(values["color.r"] * 255))),
                description()
            except OverflowError:
                print "Line: OverflowError"

        elif stype == "point":
            cv2.rectangle(
                mat,
                (int(values["x"] - 2), int(values["y"] - 2)),
                (int(values["x"] + 2), int(values["y"] + 2)),
                (int(values["color.b"] * 255),
                 int(values["color.g"] * 255),
                 int(values["color.r"] * 255)))
            description()

        elif stype == "dot":
            cv2.circle(
                mat,
                (int(values["x"]), int(values["y"])),
                3,
                (int(values["color.b"] * 255),
                 int(values["color.g"] * 255),
                 int(values["color.r"] * 255)))
            description()

        elif stype == "circle":
            cv2.circle(
                mat,
                (int(values["x"]), int(values["y"])),
                int(values["radius"]),
                (int(values["color.b"] * 255),
                 int(values["color.g"] * 255),
                 int(values["color.r"] * 255)))
            description()

        elif stype == "robot":
            cv2.circle(
                mat,
                (int(values["x"]), int(values["y"])),
                int(5),  # Komisch mal gucken
                (int(values["color.b"] * 255),
                 int(values["color.g"] * 255),
                 int(values["color.r"] * 255)))
            cv2.line(
                mat,
                (int(values["x"]), int(values["y"])),
                (int(values["x"] + 15*(cos(values["rot"] + 0.5)))
                , int(values["y"] + 15*(sin(values["rot"] + 0.5)))),
                (int(values["color.b"] * 255),
                 int(values["color.g"] * 255),
                 int(values["color.r"] * 255))),
            cv2.line(
                mat,
                (int(values["x"]), int(values["y"])),
                (int(values["x"] + 15*(cos(values["rot"] - 0.5)))
                , int(values["y"] + 15*(sin(values["rot"] - 0.5)))),
                (int(values["color.b"] * 255),
                 int(values["color.g"] * 255),
                 int(values["color.r"] * 255))),
            description()

        elif stype == "rect":
            cv2.rectangle(
                mat,
                (int(values["x"]), int(values["y"])),
                (int(values["x"] + values["width"]
                     ), int(values["y"] + values["height"])),
                (int(values["color.b"] * 255),
                 int(values["color.g"] * 255),
                 int(values["color.r"] * 255)))
            description()

        elif stype == "text":
                cv2.putText(
                    mat,
                    values["text"],
                    (int(values["x"]), int(values["y"])),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (int(values["color.b"] * 255),
                        int(values["color.g"] * 255),
                        int(values["color.r"] * 255)))
