# -*- coding:utf-8 -*-
"""
VisualizationDrawerModule
^^^^^^^^^^^^^^^^^^^^^^^^^

Visualize different vision information directly on the image. A interactive control by hotkeys is provided.

History:
''''''''
* 27.04.15: Extracted from vision script (Marc)
* 16.05.15: Finished work on the ground structure (Marc)
"""
import os
import cv
import sys

import cv2

from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_DATA_CAMERA, DATA_KEY_IMAGE_PATH, DATA_KEY_RAW_IMAGE
from bitbots.modules.keys.visualization_keys import VIZ_KEY_VIZ_ACTIVE, VIZ_KEY_NUMBER_IMAGES, VIZ_KEY_INDEX_IMAGE, \
    VIZ_KEY_CANDIDATE_SHAPES, VIZ_KEY_RATED_OUT_SHAPES, VIZ_KEY_ORANGE_BALL_SHAPE, VIZ_KEY_BODY_OUT_SHAPES, \
    VIZ_KEY_SMALL_OUT_SHAPES, VIZ_KEY_HUGE_OUT_SHAPES, VIZ_KEY_FAR_OUT_SHAPES, VIZ_KEY_REQUEST_NEW_FRAME, \
    VIZ_KEY_BALL_POSSIBLE_LIST_SHAPE, VIZ_KEY_GOAL_CANDIDATE_SHAPES, VIZ_KEY_GOAL_SORTED_OUT_SHAPES, \
    VIZ_KEY_GOAL_FINAL_SHAPE, VIZ_KEY_CURRENT_FRAME, VIZ_KEY_ACTIVE_FEATURES
from bitbots.util.make_cairo_shapes import line, draw_shapes


image_path = None

class VisualizationModule(AbstractModule):

    def start(self, data):
        # activate visualization in other modules
        data[VIZ_KEY_VIZ_ACTIVE] = True
        data[VIZ_KEY_ACTIVE_FEATURES] = []

        # check if source is files or camera
        if image_path is not None:
            data[DATA_KEY_DATA_CAMERA] = True
            data[DATA_KEY_IMAGE_PATH] = image_path
        else:
            print "Direct camera is not yet implmentend"
            sys.exit(1)

        # different visiualization possibilities
        self.current_index = 0
        self.number_images = 0
        self.color = False #todo make this work
        self.middle_line = False

        self.ball_active = False
        self.ball_candidates = False
        self.ball_orange_bypass = False
        self.balls_on_body = False
        self.rated_ball = False
        self.small_ball = False
        self.huge_ball = False
        self.far_ball = False
        self.ball_list = False

        self.goal_active = False
        self.goal_candidate = False
        self.goals_sorted = False
        self.final_goal = False

        #todo add a possibilty to start with predefined values for displayed shapes

        # Make a window for the viz
        cv.NamedWindow("Visualization", flags=cv2.CV_WINDOW_AUTOSIZE)

        #todo
        """
        directes camerabild aber als eigenes modul

        color image (key c)

        horizont usw in einzelnen modulen auch einbaun"""

    def update(self, data):
        # a hack to make sure the camera module provieded data, refactor if you know a better solution
        if data.get(VIZ_KEY_NUMBER_IMAGES, False):
            self.number_images = data[VIZ_KEY_NUMBER_IMAGES]
        else:
            return

        # request a new frame from the data camera
        data[VIZ_KEY_REQUEST_NEW_FRAME] = True

        if data[DATA_KEY_RAW_IMAGE] is None:
            print "no raw image"
            return

        data[VIZ_KEY_CURRENT_FRAME] = self.current_index
        self.draw_image(data)

        # wait for keyboard input
        key = cv2.waitKey(1000000)
        self.handle_keyboard_input(data, key)


    def draw_image(self, data):
        # collects all shapes that are wanted by the user

        image = data[DATA_KEY_RAW_IMAGE]

        if not self.color:
            image = image[:, ::2]

        height, width = image.shape[:2]

        shapes = []
        if self.middle_line:
            shapes.extend(line(0, height / 2, width, height / 2, 0, 0, 0, 3))

        if self.ball_active:
            if self.ball_candidates:
                shapes.extend(data[VIZ_KEY_CANDIDATE_SHAPES])
            if self.ball_orange_bypass:
                shapes.extend(data[VIZ_KEY_ORANGE_BALL_SHAPE])
            if self.rated_ball:
                shapes.extend(data[VIZ_KEY_RATED_OUT_SHAPES])
            if self.balls_on_body:
                shapes.extend(data[VIZ_KEY_BODY_OUT_SHAPES])
            if self.small_ball:
                shapes.extend(data[VIZ_KEY_SMALL_OUT_SHAPES])
            if self.huge_ball:
                shapes.extend(data[VIZ_KEY_HUGE_OUT_SHAPES])
            if self.far_ball:
                shapes.extend(data[VIZ_KEY_FAR_OUT_SHAPES])
            if self.ball_list:
                shapes.extend(data[VIZ_KEY_BALL_POSSIBLE_LIST_SHAPE])

        if self.goal_active:
            if self.goal_candidate:
                shapes.extend(data[VIZ_KEY_GOAL_CANDIDATE_SHAPES])
            if self.goals_sorted:
                shapes.extend(data[VIZ_KEY_GOAL_SORTED_OUT_SHAPES])
            if self.final_goal:
                shapes.extend(data[VIZ_KEY_GOAL_FINAL_SHAPE])

        image = draw_shapes(image, shapes)

        cv2.imshow("Visualization", image[:, :, :3].copy())

    def handle_keyboard_input(self, data, key):

        if key in (27, 1048603):
            # Zeikeyen ist Strg-c oder Strg-d, abbrekeyen
            #todo trotzdem noch sachen tun wie statistik anzeigen
            raise KeyboardInterrupt("Exit on user request")

        if key is isinstance(key, basestring):
            pass

        elif key == ord('a'):
            if self.current_index > 0:
                self.current_index -= 1
        elif key == ord('d'):
            if self.current_index < self.number_images - 1:
                self.current_index += 1
        elif key == ord('w'):
            if self.current_index < self.number_images - 10:
                self.current_index += 10
        elif key == ord('s'):
            if self.current_index > 10:
                self.current_index -= 10
        elif key == ord('q'):
            self.current_index = 0
        elif key == ord('e'):
            self.current_index = self.number_images - 1

        # toggle color
        elif key == ord('c'):
            self.color = not self.color
        elif key == ord('y'):
            self.middle_line = not self.middle_line

        # toggle all ball shapes
        elif key == ord('b'):
            self.ball_active = not self.ball_active

        # toggle single ball shapes
        elif key == ord('t'):
            self.ball_candidates = not self.ball_candidates
        elif key == ord('z'):
            self.rated_ball = not self.rated_ball
        elif key == ord('u'):
            self.balls_on_body = not self.balls_on_body
        elif key == ord('i'):
            self.ball_orange_bypass = not self.ball_orange_bypass
        elif key == ord('o'):
            self.small_ball = not self.small_ball
        elif key == ord('h'):
            self.huge_ball = not self.huge_ball
        elif key == ord('j'):
            self.far_ball = not self.far_ball
        elif key == ord('l'):
            self.ball_list = not self.ball_list

        # toggle all goal shapes
        elif key == ord('g'):
            self.goal_active = not self.goal_active
        elif key == ord('v'):
            self.goal_candidate = not self.goal_candidate
        elif key == ord('n'):
            self.goals_sorted = not self.goals_sorted
        elif key == ord('m'):
            self.final_goal = not self.final_goal
        else:
            print "The key you pressed has no function."

        # When any goal or ball option is enabled, then we activate the base feature
        if self.goal_candidate or self.final_goal or self.goals_sorted:
            self.goal_active = True
        if self.ball_candidates or self.rated_ball or self.balls_on_body or \
                self.ball_orange_bypass or self.small_ball or self.huge_ball or \
                self.far_ball or self.ball_list:
            self.ball_active = True

        data[VIZ_KEY_ACTIVE_FEATURES] = [key for key in self.__dict__ if self.__dict__[key] is True]
        # tell the camera module about it
        data[VIZ_KEY_INDEX_IMAGE] = self.current_index

def register(ms):
    ms.add(VisualizationModule, "Visualization",
           requires=[],
           provides=[])
