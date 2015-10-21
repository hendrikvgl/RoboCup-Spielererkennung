# -*-coding:utf-8 -*-
import cv2


class ImageView(object):
    FACTOR = 5  # scale for shapes

    def __init__(self, destroy):
        self.destroy = destroy
        self.last_image = None
        self.last_shapes = None
        self.last_width = self.last_height = None

    def cleanup(self):
        pass

    def update(self, item):
        pass

    def register_observers(self, name, register):
        self.name = name
        cv2.namedWindow(name, cv2.cv.CV_WINDOW_NORMAL)
        register(name, lambda item: setattr(self, "last_image", item.value))
        register(name + ".Shapes", lambda item: setattr(self,
                 "last_shapes", item.value))
        register(name + ".Draw", lambda item: self.draw())

    def draw(self):
        """draw new image whenever one arrives
        """
        if self.last_image is None:
            return
        #Hack to check if the window was closed:
        try:
            cv2.getWindowProperty(self.name, 0)
        except:
            self.destroy()
            return
        # The arriving image does not support color, so we convert it
        img = cv2.cvtColor(self.last_image, cv2.COLOR_GRAY2RGB)
        # The arriving image is pretty small, we change that here
        mat = cv2.resize(img, (0, 0), fx=self.FACTOR, fy=self.FACTOR)
        # Now we draw the debug-shapes
        if self.last_shapes is not None:
            draw_debug_shapes(mat, self.last_shapes)
        # When that is done all that is left is show the image
        cv2.imshow(self.name, mat)


def draw_debug_shapes(mat, shapes):
    """Draw set of debug shapes on the image mat
    """
    for shape in shapes:
        stype, values = shape
        if not all(v == v for v in values.values()):
            # filter out NaN
            continue

        def description():
            """Puts description text of this item in the picture
            """
            if not values.get("text", ""):
                return
                cv2.putText(
                    mat,
                    values["text"],
                    (int(values["x"] + 3), int(values["y"] + 10))
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
                    (int(values["x"]), int(values["y"]))
                    (int(values["color.b"] * 255),
                        int(values["color.g"] * 255),
                        int(values["color.r"] * 255)))
