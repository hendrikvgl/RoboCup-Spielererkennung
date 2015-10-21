# -*- coding:utf-8 -*-
"""
BallVisualizationModule
^^^^^^^^^^^^^^^^^^^^^^^

Generates the Cairo shapes for visualization.


History:
''''''''
* 26.04.15. Extracted from vision script (Marc)
"""
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.keys import DATA_KEY_RAW_GOAL_DATA, DATA_KEY_GOAL_INFO, DATA_KEY_CAMERA_RESOLUTION
from bitbots.modules.keys.visualization_keys import VIZ_KEY_SORTED_OUT_GOALS, VIZ_KEY_GOAL_CANDIDATE_SHAPES, \
    VIZ_KEY_GOAL_SORTED_OUT_SHAPES, VIZ_KEY_GOAL_FINAL_SHAPE
from bitbots.util.make_cairo_shapes import white_rectangle, red_rectangle, big_red_text, yellow_rectangle


class GoalVisualizationModule(AbstractModule):

    def start(self, data):
        self.width, self.height = data[DATA_KEY_CAMERA_RESOLUTION]

    def update(self, data):
        data[VIZ_KEY_GOAL_CANDIDATE_SHAPES] = self.make_goal_candidate_shapes(data, self.width, self.height)
        data[VIZ_KEY_GOAL_SORTED_OUT_SHAPES] = self.make_goal_sorted_shapes(data, self.width, self.height)
        data[VIZ_KEY_GOAL_FINAL_SHAPE] = self.make_final_goal_shape(data, self.width, self.height)

    def make_goal_candidate_shapes(self, data, width, height):
        goal_array = data.get(DATA_KEY_RAW_GOAL_DATA, None)
        if goal_array is None:
            return []
        posts, color = goal_array
        shapes = []
        for post in posts:
            x, y, w_rel, w, h = post
            x, y, w, h = make_rect(x, y, w, h, width, height)

            shapes.extend(white_rectangle(x, y, w, h))
        return shapes

    def make_goal_sorted_shapes(self, data, width, height):
        shapes = []
        for dataset in data.get(VIZ_KEY_SORTED_OUT_GOALS, []):
            # mark as white
            x = dataset[1]
            y = dataset[2]
            w = dataset[3]
            h = dataset[4]

            x, y, w, h = make_rect(x, y, w, h, width, height)
            if dataset[0] == "X" or dataset[0] == "XE":
                shapes.extend(red_rectangle(x, y, w, h))
            x += w +5
            y += h/2

            shapes.extend(big_red_text(x, y, dataset[0]))
        return shapes

    def make_final_goal_shape(sefl, data, width, height):
        goal = data.get(DATA_KEY_GOAL_INFO, None)
        if goal is None:
            return []
        shapes = []
        index = 0
        for post in goal: #todo dafug?
            x = goal[index].x
            y = goal[index].y
            w = goal[index].width
            h = goal[index].height
            index +=1

            shapes.extend(yellow_rectangle(x, y, w, h))
        return shapes

def make_rect(x, y, w, h, width, height):
    x /= -1
    y *= -1
    x = x * width
    y = y * width
    x += width * 0.5
    y += height * 0.5
    w = w * width
    h = h*height

    y -= h
    x -= (w/2)

    return x, y, w, h

def register(ms):
    ms.add(GoalVisualizationModule, "GoalVisualization",
           requires=[DATA_KEY_CAMERA_RESOLUTION],
           provides=[])
