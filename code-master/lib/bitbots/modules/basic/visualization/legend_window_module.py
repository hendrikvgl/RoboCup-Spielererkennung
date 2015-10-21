# -*- coding:utf-8 -*-
"""
LegendWindowModule
^^^^^^^^^^^^^^^^^^

Displays the legend window for visualization


History:
''''''''
* 16.05.15. Extracted from visualization module (Marc)
"""
import cv
import cv2
import numpy as np
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys.visualization_keys import VIZ_KEY_BALL_LEGEND, VIZ_KEY_BEST_BALL_NUMBER, \
    VIZ_KEY_BALL_STATISTIC, VIZ_KEY_NUMBER_IMAGES, VIZ_KEY_INDEX_IMAGE, VIZ_KEY_CURRENT_FRAME, VIZ_KEY_ACTIVE_FEATURES
from bitbots.util.make_cairo_shapes import green_text, white_text_block, red_text, list_text, white_text, white_line, \
    draw_shapes


class LegendWindowModule(AbstractModule):

    def start(self, data):
        self.height = 400
        self.width = 800
        self.nr_colums = 5

        cv.NamedWindow("Legend")
        leg_im = np.zeros((self.height, self.width), np.uint8)
        cv2.imshow("Legend", leg_im)

    def update(self, data):

        self.draw_legend(data)

    def draw_legend(self, data):

        leg_im = np.zeros((self.height, self.width), np.uint8)
        current_index = data.get(VIZ_KEY_CURRENT_FRAME, 0)
        number_images = data.get(VIZ_KEY_NUMBER_IMAGES, 0)

        #start position on the image
        x_start = 5
        y_start = 15
        shapes = []

        # Header
        shapes.extend(self.legend_header(self.width, self.nr_colums, x_start, y_start))
        x = x_start
        y = y_start + 20

        # General information
        if current_index != 0 and current_index != number_images - 1:
            shapes.extend(green_text(x, y, "Frame: %d of %d " % (current_index, number_images - 1)))
        else:
            shapes.extend(red_text(x, y, "Frame: %d of %d " % (current_index, number_images - 1)))

        #todo further stuff? maybe a statistic of seen balls until this bpoint

        # Ball information
        x = self.width/self.nr_colums + x_start

        shapes.extend(white_text_block(x, y, data[VIZ_KEY_BALL_STATISTIC]))

        texts = data[VIZ_KEY_BALL_LEGEND]
        shapes.extend(list_text(x, y, texts))
        chosen_text = "Chosen Ball: " + str(data.get(VIZ_KEY_BEST_BALL_NUMBER, []))
        shapes.extend(green_text(x, self.height - 10, chosen_text))

        # Goal informatiion
        x = 2 * self.width/self.nr_colums + x_start
        #todo add some meaningful information about the goals

        # Active features for visualization:
        activate_features = data[VIZ_KEY_ACTIVE_FEATURES]
        # Key bindings #todo only if datapictures
        x = 3 * self.width/self.nr_colums + x_start

        def active(key, features):
            k = key.lower()[3:].replace(" ", "_")
            if True in [(k in f or f in k) for f in features]:
                key = "x " + key
            else:
                key = key + "  "
            return key
        a = lambda k: active(k, activate_features)

        key_binding_string1 = [a("d: Image index + 1"),
                              a("a: Image index -1"),
                              a("w: Image index +10"),
                              a("s: Image index -10"),
                              a("e: Jump to end"),
                              a("q: Jump tp start"),
                              "",
                              a("c: Color/BW Image"),
                              a("y: middle line"),
                              "",
                              a("b: All Ball Viz"),
                              a("t: Ball candidates"),
                              a("z: Bad rated balls"),
                              a("u: Balls on body"),
                              a("i: Orange bypass"),
                              a("o: To small balls"),
                              a("h: To huge balls"),
                              a("j: To far balls"),
                              a("l: No. in chosen list"),
                              ""]

        key_binding_string2 = [a("g: All goal viz"),
                               a("v: Goal candidates"),
                               a("n: Goals sorted out"),
                               a("m: Final goal")]

        shapes.extend(white_text_block(x, y, key_binding_string1))
        x = 4 * self.width/self.nr_colums + x_start
        shapes.extend(white_text_block(x, y, key_binding_string2))

        leg_im = draw_shapes(leg_im, shapes)
        cv2.imshow("Legend", leg_im)


    def legend_header(self, width, nr_colums, x_start, y_start):
        x = x_start
        y = y_start

        shapes = []
        shapes.extend(white_text(x, y, "General Information"))
        x += width/nr_colums
        shapes.extend(white_text(x, y, "Ball Information"))
        x += width/nr_colums
        shapes.extend(white_text(x, y, "Goal Information"))
        x += width/nr_colums
        shapes.extend(white_text(x, y, "Key Bindings"))
        x += width/nr_colums
        shapes.extend(white_text(x, y, "")) #still keybining
        y += 3
        shapes.extend(white_line(0, y, width, y))

        return shapes



def register(ms):
    ms.add(LegendWindowModule, "LegendWindow",
           requires=[],
           provides=[])
