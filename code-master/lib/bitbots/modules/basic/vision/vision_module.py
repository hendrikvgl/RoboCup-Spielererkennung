#-*- coding:utf-8 -*-
"""
VisionModule
^^^^^^^^^^^^

Das Vision Module verfüttert die Bilder an die Vision um Verschidene
Daten zu extrahieren

History:
''''''''

* ??.??.??: Erstellt (Nils Rokita)

* 21.12.2013: Das VisionModule und die Vision unterstützen den Export von den Benutzen Farbmasken (Robert Schmidt)

* 06.08.14 Refactor (Marc Bestmann)
"""
import time
from bitbots.debug.debug_decorator import Debug, ComplexObjectConverter
from bitbots.debug.debuglevels import DebugLevel
from bitbots.modules.basic.vision.vision_objects import ObstacleInfo, GoalInfo
from bitbots.debug.timer import Timer
import gzip
import json
import os

from bitbots.modules.keys import DATA_KEY_GOAL_FOUND, DATA_KEY_GOAL_INFO, DATA_KEY_IS_NEW_FRAME, \
    DATA_KEY_GIVE_UP_GOAL, DATA_KEY_CONFIG, DATA_KEY_CURRENT_HORIZON_UV, DATA_KEY_CURRENT_HORIZON_ORIENTATION, \
    DATA_KEY_OBSTACLE_FOUND, DATA_KEY_OBSTACLE_INFO, DATA_KEY_RAW_BALL, DATA_KEY_TRANSFORMER, \
    DATA_KEY_CAMERA_FRAME_VERSION, DATA_KEY_RAW_IMAGE, DATA_KEY_IMAGE_POSE, DATA_KEY_IMAGE_FORMAT, \
    DATA_KEY_CAMERA_EXPOSURE_CALLBACK, DATA_KEY_RECALIBRATE_BALL, DATA_KEY_CAMERA_FOOT_PHASE, DATA_KEY_CAMERA_RESOLUTION, \
    DATA_KEY_LINE_POINTS, DATA_KEY_SUPPORT_LEG, DATA_KEY_HORIZON_OBSTACLES, DATA_KEY_ANY_WHOLE_GOAL_LAST_SEEN, \
    DATA_KEY_TRANSFORMER_UPDATED, DATA_KEY_IGNORE_MASQ_HITS, DATA_KEY_ANY_GOALPOST_LAST_SEEN, DATA_KEY_IPC, \
    DATA_KEY_RAW_GOAL_DATA
from bitbots.util import find_resource
from bitbots.modules.abstract import AbstractModule
from bitbots.modules.abstract.abstract_module import debug_m
import bitbots.vision.robotvision as rv
from bitbots.vision.robotvision import RobotVision
from bitbots.locator.transformer import Transformer
from bitbots.util.png import PngImage
from bitbots.util.png import save_png_image
from bitbots.util.kinematicutil import get_robot_horizon_p, get_robot_horizon_r
from bitbots.util import get_config

config = get_config()


# Definitionen für color fom Obstracle Info
OBSTACLE_UNKNOWN = rv.OBSTACLE_UNKNOWN()
OBSTACLE_MAGENTA = rv.OBSTACLE_MAGENTA()
OBSTACLE_ONLY_MAGENTA = rv.OBSTACLE_ONLY_MAGENTA()
OBSTACLE_CYAN = rv.OBSTACLE_CYAN()
OBSTACLE_ONLY_CYAN = rv.OBSTACLE_ONLY_CYAN()
OBSTACLE_ONLY_COLOR = rv.OBSTACLE_ONLY_COLOR()

import numpy


class VisionModule(AbstractModule):
    """Verhalten zur suche vom Ball"""

    def __init__(self):
        self.last_frame_version = 0
        self.last_ball_info = None
        self.idx=0


    def start(self, data):
        config = get_config()
        self.max_ball_distance = config['field']['length'] + 2000
        config = config["vision"]
        self.export_frame_skip = config["export_every_n_th_frame"]
        self.ball_pos_is_ball_footpoint = config["ball_pos_is_ball_footprint"]
        color_config = self.load_color_config(config["VISION_COLOR_CONFIG"])
        tr_config = config["vision-thresholds"]
        width, heigth = data[DATA_KEY_CAMERA_RESOLUTION]
        self.use_kinematic_horizon = config["use_kinematic_horizon"]
        self.vision = RobotVision(tr_config["green_y"],
                                  tr_config["green_u"], tr_config["green_v"],
                                  tr_config["green_dynamic"], width, heigth, config["vision-ignore_goals_out_of_field"])
        self.vision.set_color_config(color_config)

        self.vision.set_ball_enabled(config["vision-ball_enabled"])
        self.vision.set_goals_enabled(config["vision-goals_enabled"])
        self.vision.set_lines_enabled(config["vision-lines_enabled"])
        self.vision.set_pylons_enabled(config["vision-pylons_enabled"])
        self.vision.set_shape_vectors_enabled(
            config["vision-shape_vectors_enabled"])
        self.vision.set_team_marker_enabled(config["vision-team_marker_enabled"])
        self.vision.set_is_picture_inverted(config["invertetPicture"])
        self.vision.set_ball_pos_is_ball_footpoint(self.ball_pos_is_ball_footpoint)
        self.vision.set_rgb_step_factor(config["RGB_STEP_FACTOR"])
        self.vision.set_b_w_debug_image(config["SEND_BW_DEBUG"])

        self.vision.set_min_intensity(config["vision-intensity-min"])
        self.vision.set_max_intensity(config["vision-intensity-max"])

        # setzen des erwarteten bildformates
        self.vision.set_image_format(data[DATA_KEY_IMAGE_FORMAT])

        self.transformer = Transformer()
        data[DATA_KEY_TRANSFORMER] = self.transformer
        self.transformer.set_camera_angle(config["CameraAngle"])
        self.vision.set_camera_exposure_callback(data["CameraExposureCalback"])
        data[DATA_KEY_CAMERA_EXPOSURE_CALLBACK] = None
        data[DATA_KEY_SUPPORT_LEG] = 0
        data[DATA_KEY_OBSTACLE_FOUND] = False

        # obstacle infos --- veraltet
        # self.extract_obstacle_infos(data, self.vision.obstacles)

        data[DATA_KEY_GOAL_FOUND] = 0
        data[DATA_KEY_GOAL_INFO] = None
        data[DATA_KEY_OBSTACLE_FOUND] = 0
        data[DATA_KEY_OBSTACLE_INFO] = []

        #if do_not_override:
        if os.path.exists("/home/darwin"):
            files=os.listdir("/home/darwin")
            while "frame-%04d.yuv" % self.idx in files:
                self.idx = self.idx + 1

    def load_color_config(self, which):
        # Farbraum-Konfiguration laden
        conf = numpy.zeros((256, 768), dtype=numpy.uint8)
        for idx, name in enumerate(("ball", "cyan", "yellow", "carpet", "white", "magenta")):
            if name != "carpet":  # ignoring carpet, because of autoconfig
                debug_m(DebugLevel.LEVEL_4, "searching vision-color-config/%s/%s.png" % (which, name))
                name = find_resource(
                    "vision-color-config/%s/%s.png" % (which, name))
                debug_m(DebugLevel.LEVEL_4, "Loading %s" % name)
                im = PngImage(name)
                mask = im.get_png_as_numpy_array()
                mask[mask != 0] = (1 << idx)
                conf += mask
                debug_m(DebugLevel.LEVEL_4, "vision-color-config/%s/%s.png geladen" % (which, name))
            else:
                debug_m(DebugLevel.LEVEL_4, "vision-color-config/%s/%s.png ignoriert (autocolorconfig)" % (which, name))

        return conf

    def save_color_config(self, name="ball"):
        config = self.vision.get_color_config(name)
        path = find_resource("vision-color-config/auto-color-config")
        save_png_image("%s/%s.png" % (path, name), config)

    def extract_obstacle_infos(self, data, obstacles_from_vision):
        """ This method is extracting a lot of information from the results the vision has given """
        debug_m(4, "ObstacleNumber", len(obstacles_from_vision))
        if not obstacles_from_vision:
            data[DATA_KEY_OBSTACLE_FOUND] = False
            debug_m(4, "ObstacleFound", False)
            return
        else:
            data[DATA_KEY_OBSTACLE_FOUND] = True
            debug_m(4, "ObstacleFound", True)
            obstacles = []
            i = 0
            for ob_data in obstacles_from_vision:
                x, y, h, w, result = ob_data
                u, v = self.transformer.transform_point_to_location(x, y, 0)
                u = int(u)
                v = int(v)

                ob_info = ObstacleInfo(*[u, v, x, y, h, w, result])
                obstacles.append(ob_info)
                debug_m(4, "Obstacle.%d.u" % i, u)
                debug_m(4, "Obstacle.%d.v" % i, v)
                debug_m(4, "Obstacle.%d.colour" % i, result)
                i += 1
            data[DATA_KEY_OBSTACLE_INFO] = obstacles

    def extract_horizon_obstacles(self, data, obstacles):
        obstacles = [self.transformer.transform_point_to_location(obs[0], obs[1], 0.0) for obs in obstacles]
        data[DATA_KEY_HORIZON_OBSTACLES] = obstacles
        i = 0
        for obstacle in obstacles:
            debug_m(4, "Obstacle.%d.u" % i, obstacle[0])
            debug_m(4, "Obstacle.%d.v" % i, obstacle[1])
            i += 1
        debug_m(4, "AnzObstacles", len(obstacles))
        data[DATA_KEY_OBSTACLE_FOUND] = len(obstacles) > 0

    def check_is_new_frame(self, data):
        """ This method checks if there is a new frame available """
        if self.last_frame_version >= data[DATA_KEY_CAMERA_FRAME_VERSION]:
            return False
        else:
            self.last_frame_version = data[DATA_KEY_CAMERA_FRAME_VERSION]
            supportLeg = self.transformer.update_pose(data[DATA_KEY_IMAGE_POSE])
            data[DATA_KEY_TRANSFORMER_UPDATED] = True
            data[DATA_KEY_SUPPORT_LEG] = supportLeg
            return True

    def extract_horizon_line_properties(self, data):
        # Get the current horizon
        c_horizon_x, c_horizon_y = self.vision.get_current_relativ_horizon()
        c_horizon_u, c_horizon_v = self.transformer.transform_point_to_location(0, c_horizon_y, 0)

        data[DATA_KEY_CURRENT_HORIZON_UV] = [c_horizon_u, c_horizon_v]
        data[DATA_KEY_CURRENT_HORIZON_ORIENTATION] = c_horizon_x


    """    @Debug(update_time=0.5, list_of_data_keys= {
        DebugLevel.DURING_GAME_DEBUG: [
            DATA_KEY_GOAL_FOUND,
            DATA_KEY_OBSTACLE_FOUND,
        ],

        DebugLevel.GAME_PREPARE_DEBUG: [
            (DATA_KEY_GOAL_INFO, ComplexObjectConverter.convert_goal_info),
            # TODO define a converter
            (DATA_KEY_OBSTACLE_INFO, ComplexObjectConverter.convert_nothing)
        ]
    })
    """

    def update(self, data):
        """ This Method checks if there is new data to process and if so let the
            robot vision process the image and extract data for further behaviour """
        if not self.check_is_new_frame(data):
            data[DATA_KEY_IS_NEW_FRAME] = False
            return
        else:
            data[DATA_KEY_IS_NEW_FRAME] = True
            need_to_recalibrate_ball_config = data[DATA_KEY_RECALIBRATE_BALL]
            # Process the Image
            if self.use_kinematic_horizon:
                robo_horizon_k = get_robot_horizon_p(self.transformer.robot, data[DATA_KEY_CAMERA_FOOT_PHASE])
                robo_horizon_imu = get_robot_horizon_r(self.transformer.robot , data[DATA_KEY_IPC].get_robot_angle()) \
                                    if data.get(DATA_KEY_IPC, False) else robo_horizon_k
                #print robo_horizon_k - robo_horizon_imu
                robo_horizon = (robo_horizon_k + robo_horizon_imu) / 2
                #robo_horizon = robo_horizon_k
                robo_horizon[1] = robo_horizon[1] / self.transformer.get_camera_angle()
                self.vision.set_robot_horizon(robo_horizon / self.transformer.get_camera_angle())
            self.vision.process(data[DATA_KEY_RAW_IMAGE], need_to_recalibrate_ball_config)
            if need_to_recalibrate_ball_config is True:
                self.save_color_config("ball")

            # Get the Informations from the Cython Class
            data[DATA_KEY_RAW_BALL] = self.vision.ball_info
            goal_info = self.vision.goal_info
            data[DATA_KEY_RAW_GOAL_DATA] = goal_info
            obstacles = self.vision.obstacle

            # Pass the Information to the extractor
            #self.extract_goal_infos(data, goal_info)
            self.extract_horizon_obstacles(data, obstacles)
            self.extract_horizon_line_properties(data)

            data[DATA_KEY_IGNORE_MASQ_HITS] = self.vision.ignore_masq_hits
            #debug_m(5, "IgnoreMasq", self.vision.ignore_masq_hits)
            data[DATA_KEY_LINE_POINTS] = self.vision.line_points
            #debug_m(5, "NumberLinePoints", data["LinePoints"].size)

            if self.export_frame_skip > 0 and data[DATA_KEY_CAMERA_FRAME_VERSION] % self.export_frame_skip is 0:
                # Dateiname für den nächsten Frame
                name = "frame-%04d.yuv" % self.idx
                self.idx += 1
                with Timer("Speichere " + name, self.debug):
                    yuyv = data[DATA_KEY_RAW_IMAGE]

                    with open("/home/darwin/" + name + ".json", "wb") as fp:
                        angle = data[DATA_KEY_IPC].get_robot_angle()
                        json.dump({"positions": data[DATA_KEY_IMAGE_POSE].positions, "robot_angle": [angle.x, angle.y, angle.z]}, fp)

                    with gzip.GzipFile("/home/darwin/" + name + ".gz", "wb", compresslevel=1) as fp:
                        fp.write(yuyv.tostring())


def register(ms):
    ms.add(VisionModule, "Vision",
           requires=[DATA_KEY_RAW_IMAGE,
                     DATA_KEY_IMAGE_POSE,
                     DATA_KEY_CAMERA_FRAME_VERSION,
                     DATA_KEY_IMAGE_FORMAT,
                     DATA_KEY_CONFIG,
                     DATA_KEY_CAMERA_EXPOSURE_CALLBACK,
                     DATA_KEY_RECALIBRATE_BALL,
                     DATA_KEY_CAMERA_FOOT_PHASE,
                     DATA_KEY_CAMERA_RESOLUTION],
           provides=[DATA_KEY_GOAL_FOUND,
                     DATA_KEY_GOAL_INFO,
                     DATA_KEY_IS_NEW_FRAME,
                     DATA_KEY_LINE_POINTS,
                     DATA_KEY_OBSTACLE_FOUND,
                     DATA_KEY_OBSTACLE_INFO,
                     DATA_KEY_SUPPORT_LEG,
                     DATA_KEY_RAW_BALL,
                     DATA_KEY_TRANSFORMER,
                     DATA_KEY_CURRENT_HORIZON_UV,
                     DATA_KEY_CURRENT_HORIZON_ORIENTATION,
                     DATA_KEY_HORIZON_OBSTACLES,
                     DATA_KEY_TRANSFORMER_UPDATED,
                     DATA_KEY_IGNORE_MASQ_HITS])
