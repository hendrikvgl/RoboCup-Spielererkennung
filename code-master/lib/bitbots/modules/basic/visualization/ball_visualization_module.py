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
from bitbots.modules.keys import DATA_KEY_RAW_BALL, DATA_KEY_CAMERA_RESOLUTION, DATA_KEY_BALL_INFO, DATA_KEY_BALL_FOUND
from bitbots.modules.keys.visualization_keys import VIZ_KEY_BALL_RATING_OUT, VIZ_KEY_BALL_BODY_OUT, \
    VIZ_KEY_BALL_SMALL_OUT, VIZ_KEY_BALL_HUGE_OUT, VIZ_KEY_BALL_FAR_OUT, VIZ_KEY_BALL_POSSIBLE_LIST, \
    VIZ_KEY_BEST_BALL_NUMBER, VIZ_KEY_CANDIDATE_SHAPES, VIZ_KEY_ORANGE_BALL_SHAPE, VIZ_KEY_RATED_OUT_SHAPES, \
    VIZ_KEY_BODY_OUT_SHAPES, VIZ_KEY_SMALL_OUT_SHAPES, VIZ_KEY_HUGE_OUT_SHAPES, VIZ_KEY_FAR_OUT_SHAPES, \
    VIZ_KEY_BALL_STATISTIC, VIZ_KEY_BALL_POSSIBLE_LIST_SHAPE, VIZ_KEY_BALL_LEGEND
from bitbots.util import get_config
from bitbots.util.make_cairo_shapes import white_ball, transform_relative_to_pixel, violet_ball, red_ball, red_text, \
    white_text, blue_text, green_text, yellow_text, yellow_ball, black_filled_rect


class BallVisualizationModule(AbstractModule):
    def start(self, data):
        config = get_config()
        self.activate_orange_ball_hack = config["vision"]["orange_ball_hack"]
        self.max_distance_to_motor = config["vision"]["max_distance_to_motor"]
        self.max_ball_distance = config["vision"]["max_distance"]
        self.image_width, self.image_height = data[DATA_KEY_CAMERA_RESOLUTION]

    def update(self, data):
        shapes = []


        # todo display thresholds

        data[VIZ_KEY_CANDIDATE_SHAPES] = self.make_candidate_shapes(data)
        data[VIZ_KEY_ORANGE_BALL_SHAPE] = self.make_piped_orange_ball_shape(data)
        data[VIZ_KEY_RATED_OUT_SHAPES] = self.make_rated_out_shapes(data)
        data[VIZ_KEY_BODY_OUT_SHAPES] = self.make_body_out_shapes(data)
        data[VIZ_KEY_SMALL_OUT_SHAPES] = self.make_small_out_shapes(data)
        data[VIZ_KEY_HUGE_OUT_SHAPES] = self.make_huge_out_shapes(data)
        data[VIZ_KEY_FAR_OUT_SHAPES] = self.make_far_out_shapes(data)
        data[VIZ_KEY_BALL_STATISTIC] = self.make_statistic_shape(data)
        data[VIZ_KEY_BALL_POSSIBLE_LIST_SHAPE], data[VIZ_KEY_BALL_LEGEND] = self.make_remaining_list_shapes(data)

    def make_candidate_shapes(self, data):
        raw_ball = data.get(DATA_KEY_RAW_BALL, None)
        if raw_ball is None:
            return []

        shapes = []
        for ball in raw_ball:
            rating, (x, y, radius) = ball
            y += radius  # directly delivered footpoint from vision
            x, y, radius = transform_relative_to_pixel(x, y, radius, self.image_width, self.image_height)
            shapes.extend(white_ball(x, y, radius))
        return shapes

    def make_piped_orange_ball_shape(self, data):
        raw_ball = data.get(DATA_KEY_RAW_BALL, None)
        if raw_ball is None:
            return []

        shapes = []
        print raw_ball
        for ball in raw_ball:
            rating, (x, y, radius) = ball
            if rating == -2 and self.activate_orange_ball_hack:
                y += radius  # directly delivered footpoint from vision
                x, y, radius = transform_relative_to_pixel(x, y, radius, self.image_width, self.image_height)
                shapes.extend(violet_ball(x, y, radius))
        return shapes

    def make_rated_out_shapes(self, data):
        shapes = []
        for info in data[VIZ_KEY_BALL_RATING_OUT]:
            x, y, radius, rating = info
            x, y, radius = transform_relative_to_pixel(x, y, radius, self.image_width, self.image_height)
            shapes.extend(red_ball(x, y, radius))
            shapes.extend(red_text(x, y, "R: %.0f" % rating))
        return shapes

    def make_body_out_shapes(self, data):
        shapes = []
        for info in data[VIZ_KEY_BALL_BODY_OUT]:
            x, y, radius, dist = info
            x, y, radius = transform_relative_to_pixel(x, y, radius, self.image_width, self.image_height)
            relation = dist / self.max_distance_to_motor
            shapes.extend(red_ball(x, y, radius))
            shapes.extend(yellow_text(x, y, "B: %.2f" % relation))
        return shapes

    def make_small_out_shapes(self, data):
        shapes = []
        for info in data[VIZ_KEY_BALL_SMALL_OUT]:
            x, y, radius, radius_to_be_pic = info
            x, y, radius = transform_relative_to_pixel(x, y, self.image_width, self.image_height)
            relation = radius / radius_to_be_pic
            shapes.extend(red_ball(x, y, radius))
            shapes.extend(green_text(x, y, "S: %.2f" % relation))
        return shapes

    def make_huge_out_shapes(self, data):
        shapes = []
        for info in data[VIZ_KEY_BALL_HUGE_OUT]:
            x, y, radius, radius_to_be_pic = info
            x, y, radius = transform_relative_to_pixel(x, y, radius, self.image_width, self.image_height)
            relation = radius / radius_to_be_pic
            shapes.extend(red_ball(x, y, radius))
            shapes.extend(blue_text(x, y, "H: %.2f" % relation))
        return shapes

    def make_far_out_shapes(self, data):
        shapes = []
        for info in data[VIZ_KEY_BALL_FAR_OUT]:
            x, y, radius, dist = info
            x, y, radius = transform_relative_to_pixel(x, y, radius, self.image_width, self.image_height)
            relation = dist / self.max_ball_distance
            shapes.extend(red_ball(x, y, radius))
            shapes.extend(white_text(x, y, "F: %.0f" % relation))
        return shapes

    def make_chosen_ball_shape(self, data):
        shapes = []
        if data[DATA_KEY_BALL_FOUND]:
            ball = data[DATA_KEY_BALL_INFO]
            x, y, radius = transform_relative_to_pixel(ball.x, ball.y, ball.radius, self.image_width, self.image_height)
            shapes.extend(yellow_ball(x, y, radius))
        return shapes

    def make_remaining_list_shapes(self, data):
        shapes_on_image = []
        list = data.get(VIZ_KEY_BALL_POSSIBLE_LIST, [])

        rectangle_width = 100
        left = self.image_width - rectangle_width

        number = 0
        texts = []
        for ball in list:
            distance = ball.distance
            u = ball.u
            v = ball.v
            rating = ball.rating
            radius = ball.radius
            rating_text = "rat: %.0f" % rating
            distance_text = "Dist: %.0f" % distance
            u_text = "u: %.0f " % u
            v_text = "v: %.0f" % v
            y_start = number * 60 + 10
            start_text = "Ball " + str(number)

            x, y, radius = transform_relative_to_pixel(ball.x, ball.y, radius, self.image_width, self.image_height)

            # make white number
            shapes_on_image.extend(white_text(x, y, str(number)))

            # text for the legend
            legend_string = [start_text, rating_text, distance_text, u_text, v_text]
            texts.extend(legend_string)
            number += 1

        return shapes_on_image, texts

    def make_statistic_shape(self, data):
        raw_ball = data.get(DATA_KEY_RAW_BALL, None)
        if raw_ball is None:
            candidates = 0
        else:
            candidates = len(data[DATA_KEY_RAW_BALL])
        candidates_text = "Candidates: " + str(candidates)
        small_text = "Small balls: " + str(len(data[VIZ_KEY_BALL_SMALL_OUT]))
        big_text = "Huge balls: " + str(len(data[VIZ_KEY_BALL_HUGE_OUT]))
        far_text = "Far balls: " + str(len(data[VIZ_KEY_BALL_FAR_OUT]))
        rating_text = "Rated balls: " + str(len(data[VIZ_KEY_BALL_RATING_OUT]))
        body_text = "Body balls: " + str(len(data[VIZ_KEY_BALL_BODY_OUT]))
        possible_balls_text = "Possible balls: " + str(len(data.get(VIZ_KEY_BALL_POSSIBLE_LIST, [])))

        return [candidates_text, small_text, big_text, far_text, rating_text, body_text, possible_balls_text]


def register(ms):
    ms.add(BallVisualizationModule, "BallVisualization",
           requires=[DATA_KEY_CAMERA_RESOLUTION,
                     VIZ_KEY_BALL_RATING_OUT],
           provides=[])
