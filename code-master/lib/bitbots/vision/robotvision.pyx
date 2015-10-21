# -*- encoding: utf8 -*-
from cython.operator cimport postincrement as inc
from cython.operator cimport dereference as deref, address as ref

import numpy as np
cimport numpy as np
np.import_array()

from eigen cimport *
from debugserver cimport _Shape

from libcpp cimport bool
from libcpp.map cimport map
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.list cimport list as _list

cdef extern from "simple_vectorizer.hpp":
    cdef cppclass _Pylon "Vision::ObstacleDetection::Pylon":
        int x, y, radius

cdef extern from "simple_vectorizer.hpp":
    cdef cppclass _ShapeVector "Vision::ObstacleDetection::ShapeVector":
        int sx, sy, ex, ey, weight

cdef extern from "adapter.hpp":
    cdef cppclass _AbstractAdapter "Vision::Adapter::AbstractAdapter":
        _AbstractAdapter(MapRMatrixXb&) nogil

    cdef cppclass _RawYUYVAdapter "Vision::Adapter::RawYUYVAdapter":
        _RawYUYVAdapter(MapRMatrixXb&) nogil

    cdef cppclass _InvertedYUYVAdapter "Vision::Adapter::InvertedPictureAdapter<Vision::Adapter::RawYUYVAdapter>":
        _InvertedYUYVAdapter(MapRMatrixXb&) nogil

    cdef cppclass _RGBYUVAdapter "Vision::Adapter::RGBYUVAdapter":
        _RGBYUVAdapter(MapRMatrixXb&) nogil

    cdef cppclass _BGRYUVAdapter "Vision::Adapter::BGRYUVAdapter":
        _BGRYUVAdapter(MapRMatrixXb&) nogil

    cdef cppclass _InvertedRGBYUVAdapter "Vision::Adapter::InvertedPictureAdapter<Vision::Adapter::RGBYUVAdapter>":
        _InvertedRGBYUVAdapter(MapRMatrixXb&) nogil

    cdef cppclass _InvertedBGRYUVAdapter "Vision::Adapter::InvertedPictureAdapter<Vision::Adapter::BGRYUVAdapter>":
        _InvertedBGRYUVAdapter(MapRMatrixXb&) nogil

    cdef cppclass _IYUVAdapter "Vision::Adapter::IYUVAdapter":
        _IYUVAdapter(MapRMatrixXb&) nogil

    cdef enum _RobotDataType "Vision::Info::RobotData::DataType":
        undefined_obstacle "Vision::Info::RobotData::DataType::undefined_obstacle"
        magenta "Vision::Info::RobotData::DataType::magenta"
        much_magenta "Vision::Info::RobotData::DataType::much_magenta"
        cyan "Vision::Info::RobotData::DataType::cyan"
        much_cyan "Vision::Info::RobotData::DataType::much_cyan"
        mixed "Vision::Info::RobotData::DataType::mixed"

def OBSTACLE_UNKNOWN(): return undefined_obstacle
def OBSTACLE_MAGENTA(): return magenta
def OBSTACLE_ONLY_MAGENTA(): return much_magenta
def OBSTACLE_CYAN(): return cyan
def OBSTACLE_ONLY_CYAN(): return much_cyan
def OBSTACLE_ONLY_COLOR(): return mixed

cdef extern from "robotvision.hpp":
    cdef cppclass _BallInfo "Vision::Info::BallInfo":
        float x, y, radius, rating

    cdef cppclass _RobotData "Vision::Info::RobotData":
        float x, y, h, w
        int potential_cyan, potential_magenta
        _RobotDataType result

    cdef cppclass _GoalPost:
        float x, y, abs_height, abs_width
        int px_x, px_y, width
        bool is_foot_point_in_field

    cdef cppclass _GoalInfo "Vision::Info::GoalInfo":
        bool found()
        string color
        vector[_GoalPost] posts

    cdef cppclass _Obstacle "Vision::Info::Obstacle":
        Vector2f pos_l, pos_r

    cdef cppclass _ImageData "Vision::Info::ImageData":
        int mean_y, mean_u, mean_v

    cdef enum _MASK_TYPE "Vision::COLOR_MASK_TYPE":
        BALL "Vision::COLOR_MASK_TYPE::BALL"
        CARPET "Vision::COLOR_MASK_TYPE::CARPET"
        CYAN "Vision::COLOR_MASK_TYPE::CYAN"
        MAGENTA "Vision::COLOR_MASK_TYPE::MAGENTA"
        ALL "Vision::COLOR_MASK_TYPE::ALL"

cdef extern from "robotvision.hpp":
    cdef cppclass _RobotVision "Vision::RobotVision":
        _RobotVision(int y, int u, int v, bool dynamic, int width, int height)
        _RobotVision(int width, int height)
        void set_color_config(const_RMatrixXb&)
        void set_ball_enabled(bool enabled)
        void set_goals_enabled(bool enabled)
        void set_lines_enabled(bool enabled)
        void set_pylons_enabled(bool enabled)
        void set_team_marker_enabled(bool enabled)
        void set_b_w_debug_image(bool enabled)
        void set_min_intensity(int min)
        void set_max_intensity(int max)
        void set_rgb_step_factor(float factor)
        void set_shape_vectors_enabled(bool enabled)
        void set_ball_pos_is_ball_footpoint(bool enabled)
        void set_incremental_ball_color_config(bool incremental)
        void set_robo_horizon(const Vector2f& horizon)
        Vector2f get_relative_horizon()
        RMatrixXb get_color_config(_MASK_TYPE masq)
        char get_camera_exposure_whish()
        int get_ignore_masq_hits()

        vector[_BallInfo]& get_ball_info()
        _GoalInfo& get_goal_info()
        vector[_RobotData]& get_team_marker()
        _list[_Pylon]& get_pylons()
        _list[_ShapeVector]& get_shape_vectors()
        vector[_LineSample]& get_line_points()
        vector[_Obstacle]& get_obstacles()

        _ImageData get_image_data(_RawYUYVAdapter) nogil except +
        _ImageData get_image_data(_RGBYUVAdapter) nogil except +
        void process(_RGBYUVAdapter) nogil except +
        void process(_BGRYUVAdapter) nogil except +
        void process(_InvertedRGBYUVAdapter) nogil except +
        void process(_RawYUYVAdapter) nogil except +
        void process(_InvertedYUYVAdapter) nogil except +
        void process(_IYUVAdapter) nogil except +
        void process(_RawYUYVAdapter, bool recalibrate_ball_color, bool ignore_carpet) nogil except +
        void process(_InvertedYUYVAdapter, bool recalibrate_ball_color, bool ignore_carpet) nogil except +
        void process(_RGBYUVAdapter, bool recalibrate_ball_color, bool ignore_carpet) nogil except +
        void process(_BGRYUVAdapter, bool recalibrate_ball_color, bool ignore_carpet) nogil except +
        void process(_InvertedRGBYUVAdapter, bool recalibrate_ball_color, bool ignore_carpet) nogil except +
        void process(_IYUVAdapter, bool recalibrate_ball_color, bool ignore_carpet) nogil except +

        vector[_Shape] get_debug_shapes()

cdef class LinePoints:
    def __cinit__(self):
        self.points_available = False
        self.is_reference = False

    #Nur aufrufen, wenn man die LinePoints manuell gesetzt hat
    cdef void set_points(self, vector[_LineSample]* points, bool reference):
        if self.points_available and not self.is_reference:
            del self.points
        self.points_available = True
        self.is_reference = reference
        self.points = points

    cdef vector[_LineSample]* get_points(self) nogil:
        return self.points

    cdef bool points_set(self):
        return self.points_available

    property size:
        def __get__(self):
            if self.points_available:
                return self.points.size()
            else:
                return 0

    def __dealloc__(self):
        if self.points_available and not self.is_reference:
            del self.points

    cpdef tuple get_point(self, idx):
        cdef _LineSample elem
        if idx < self.size:
            elem = self.points.at(idx)
            return (elem.x(), elem.y())
        else:
            raise ValueError("Cannot acces LineSample at index %d" % idx)

    cpdef np.ndarray get_line_points(self):
        cdef np.ndarray r_value = np.zeros((self.size, 2), np.float)
        cdef int i = 0
        cdef int max = self.size
        while i < max:
            r_value[i] = (self.points.at(i).x(),self.points.at(i).y())
            i=i+1

        return r_value


cdef class RobotVision:
    cdef _RobotVision* vision
    cdef int decoder
    cdef char camera_exposure_wish
    cdef object camera_callback
    cdef bool inverted_picture
    cdef bool ignore_goal_out_of_field

    def __cinit__(self, int y, int u, int v, bool dynamic, int width, int height, \
                    bool ignore_goal_out_of_field=False):
        self.vision = new _RobotVision(y, u, v, dynamic, width, height)
        self.set_yuyv_decoder()
        self.inverted_picture = False
        self.camera_callback = None
        self.ignore_goal_out_of_field = ignore_goal_out_of_field

    def __dealloc__(self):
        del self.vision

    def set_color_config(self, np.ndarray arr not None):
        if arr.dtype != np.uint8 or arr.ndim != 2 or arr.shape[0] != 256 or arr.shape[1] != 768:
            raise ValueError("Invalid ColorConfig")

        cdef char *pixels = np.PyArray_BYTES(arr)
        self.vision.set_color_config(<const_RMatrixXb&>MapRMatrixXb(pixels, 256, 768))

    def get_color_config(self, object name):
        cdef _MASK_TYPE masq = CARPET
        if name == "ball":
            masq = BALL
        elif name == "carpet":
            masq = CARPET
        elif name == "all":
            masq = ALL
        else:
            return None

        cdef RMatrixXb color_config = self.vision.get_color_config(masq)
        cdef np.ndarray py_array = np.zeros((256, 768), dtype=np.uint8)
        for i in range(256):
            for j in range(768):
                py_array[i,j] = color_config.at(i,j)

        return py_array

    def set_iyuv_decoder(self):
        self.decoder = 4

    def set_bgr_decoder(self):
        self.decoder = 3

    def set_rgb_decoder(self):
        self.decoder = 2

    def set_yuyv_decoder(self):
        self.decoder = 1

    def get_current_relativ_horizon(self):
        cdef Vector2f current_horizon = self.vision.get_relative_horizon()
        return current_horizon.x(), current_horizon.y()

    def set_image_format(self, imageformat):
        if imageformat == "YUYV":
            self.set_yuyv_decoder()
        elif imageformat == "RGB":
            self.set_rgb_decoder()
        elif imageformat == "BGR":
            self.set_bgr_decoder()
        elif imageformat == "YU12":
            self.set_iyuv_decoder()
        else:
            raise ValueError("Unknown Image Format %s, cann't set decoder" %
                imageformat)

    def set_ball_enabled(self, enabled):
        self.vision.set_ball_enabled(enabled)
    def set_goals_enabled(self, enabled):
        self.vision.set_goals_enabled(enabled)
    def set_lines_enabled(self, enabled):
        self.vision.set_lines_enabled(enabled)
    def set_pylons_enabled(self, enabled):
        self.vision.set_pylons_enabled(enabled)
    def set_shape_vectors_enabled(self, enabled):
        self.vision.set_shape_vectors_enabled(enabled)
    def set_team_marker_enabled(self, enabled):
        self.vision.set_team_marker_enabled(enabled)
    def set_b_w_debug_image(self, enabled):
        self.vision.set_b_w_debug_image(enabled)
    def set_ball_pos_is_ball_footpoint(self, enabled):
        self.vision.set_ball_pos_is_ball_footpoint(enabled)
    def set_camera_exposure_callback(self, object callback):
        self.camera_callback = callback
    def set_min_intensity(self, int min):
        self.vision.set_min_intensity(min)
    def set_max_intensity(self, int max):
        self.vision.set_max_intensity(max)
    def set_rgb_step_factor(self, float factor):
        self.vision.set_rgb_step_factor(factor)
    def set_is_picture_inverted(self, bool inverted):
        self.inverted_picture = inverted
    def set_incremental_ball_color_config(self, bool incremental):
        self.vision.set_incremental_ball_color_config(incremental)
    def set_robot_horizon(self, np.ndarray horizon):
        self.vision.set_robo_horizon(Vector2f(<float>horizon[0], <float>horizon[1]))

    property camera_exposure_wish:
        def __get__(self):
            return self.camera_exposure_wish

    property ball_info:
        def __get__(self):
            cdef vector[_BallInfo]* ball_infos = ref(self.vision.get_ball_info())
            cdef list info_list = []
            if ball_infos.size() == 0:
                return None
            cdef _BallInfo info
            cdef int i = 0
            while i < ball_infos.size():
                info = ball_infos.at(i)
                info_list.append((info.rating, (info.x, info.y, info.radius)))
                i=i+1
            return info_list

    property goal_info:
        def __get__(self):
            cdef int i
            cdef _GoalInfo* info = ref(self.vision.get_goal_info())
            if not info.found():
                return None

            cdef list posts = []
            for i in range(info.posts.size()):
                if self.ignore_goal_out_of_field and not info.posts[i].is_foot_point_in_field:
                    break
                posts.append((float(info.posts[i].x), float(info.posts[i].y), info.posts[i].width, float(info.posts[i].abs_width), float(info.posts[i].abs_height)))

            return (posts, info.color.c_str()) if len(posts) is not 0 else None

    property obstacle:
        def __get__(self):
            cdef vector[_RobotData]* marker = ref(self.vision.get_team_marker())
            cdef list obstacle = []
            cdef float x, y
            cdef int num
            cdef _RobotData data
            cdef int i = 0
            while i < marker.size():
                data = marker.at(i)
                obstacle.append((
                    data.x,
                    data.y,
                    data.h,
                    data.w,
                    int(data.result)))
                i = i + 1
            return obstacle

    property obstacles:
        def __get__(self):
            cdef vector[_Obstacle]* obs = ref(self.vision.get_obstacles())
            cdef int size = obs.size(), i = 0
            cdef list obstacles = []
            while i < size:
                obstacles.append(((deref(obs)[i].pos_l.x(), deref(obs)[i].pos_l.y()), \
                                (deref(obs)[i].pos_r.x(), deref(obs)[i].pos_r.y())))
                i = i + 1
            return obstacles

    property line_points:
        def __get__(self):
            cdef vector[_LineSample]* points = new vector[_LineSample](self.vision.get_line_points())
            cdef LinePoints py_points = LinePoints()
            py_points.set_points(points, False)
            return py_points

    property ignore_masq_hits:
        def __get__(self):
            return self.vision.get_ignore_masq_hits()

    cpdef process(self, np.ndarray ndarr, bool recalibrate_ball = False, bool ignore_carpet = False, bool incremental_ball_config=False):
        cdef bool recalibrate = recalibrate_ball
        if incremental_ball_config is True:
            self.vision.set_incremental_ball_color_config(True)

        cdef MapRMatrixXb* image = vision_numpy_array_to_eigen_mat(ndarr)
        if self.decoder == 1:
            with nogil:
                if self.inverted_picture:
                    self.vision.process(_InvertedYUYVAdapter(deref(image)), recalibrate, ignore_carpet)
                else:
                    self.vision.process(_RawYUYVAdapter(deref(image)), recalibrate, ignore_carpet)
        elif self.decoder == 2:
            with nogil:
                if self.inverted_picture:
                    self.vision.process(_InvertedRGBYUVAdapter(deref(image)), recalibrate, ignore_carpet)
                else:
                    self.vision.process(_RGBYUVAdapter(deref(image)), recalibrate, ignore_carpet)
        elif self.decoder == 3:
            with nogil:
                self.vision.process(_BGRYUVAdapter(deref(image)), recalibrate, ignore_carpet)
        elif self.decoder == 4:
            with nogil:
                self.vision.process(_IYUVAdapter(deref(image)), recalibrate, ignore_carpet)
        self.camera_exposure_wish = self.vision.get_camera_exposure_whish()
        if self.camera_exposure_wish is not 0 and self.camera_callback is not None:
            self.camera_callback(self.camera_exposure_wish)
        if incremental_ball_config is True:
            self.vision.set_incremental_ball_color_config(False)

        del image

    cpdef tuple get_image_data(self, np.ndarray ndarr):
        cdef MapRMatrixXb* image = vision_numpy_array_to_eigen_mat(ndarr)
        cdef _ImageData data
        if self.decoder == 1:
            with nogil:
                data= self.vision.get_image_data(_RawYUYVAdapter(deref(image)))
        else:
            with nogil:
                data= self.vision.get_image_data(_RGBYUVAdapter(deref(image)))
        del image
        return (data.mean_y, data.mean_u, data.mean_v)

    def get_pylons(self):
        """ returns list of 3-tupel (x,y,radius)
        """
        cdef _list[_Pylon] pylons = self.vision.get_pylons()
        cdef _list[_Pylon].iterator it = pylons.begin()
        cdef list result = []
        while it != pylons.end():
            result.append((
                deref(it).x,
                deref(it).y,
                deref(it).radius
            ))
        return result

    def get_shape_vectors(self):
        """ returns list of 5-tupel (start-x,start-y,end-x,end-y,weight)
        weight is the # of pixels the vector represents.
        """
        cdef _list[_ShapeVector] shapeVectors = self.vision.get_shape_vectors()
        cdef _list[_ShapeVector].iterator it = shapeVectors.begin()
        cdef list result = []
        while it != shapeVectors.end():
            result.append((
                deref(it).sx,
                deref(it).sy,
                deref(it).ex,
                deref(it).ey,
                deref(it).weight
            ))
        return result

    def get_debug_shapes(self):
        return wrap_debug_shapes(self.vision.get_debug_shapes())

cdef class Pylon:
    cdef readonly float x, y, radius

cdef class ShapeVector:
    cdef readonly float sx, sy, ex, ey, weight
