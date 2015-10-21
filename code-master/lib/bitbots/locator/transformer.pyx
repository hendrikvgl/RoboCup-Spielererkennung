from cython.operator cimport dereference as deref
from cython.operator cimport address as ref
import numpy as np

cdef class Transformer:

    def __cinit__(self, Robot r=None):
        cdef Robot robot
        if r is not None:
            self.transformer = new _Transformer(deref(r.robot))
        else:
            robot = Robot()
            self.transformer = new _Transformer(deref(robot.robot))
            robot.robot = NULL

    def __dealloc__(self):
        del self.transformer

    cpdef update_pose(self, PyPose pose):
        return self.transformer.update_pose(deref(pose.pose))

    cpdef set_camera_angle(self, float deg):
        self.transformer.set_camera_angle(deg)

    cpdef transform_point_to_location(self, float x_point_in_picture, \
            float y_point_in_picture, float z_offset):
        #print "x: %f y: %f z: %f" % (x_point_in_picture, y_point_in_picture, z_offset)
        cdef Vector2f result = self.transformer.transform_point_with_offset( \
                Vector2f(x_point_in_picture, y_point_in_picture), z_offset / 1000.0) * 1000
        return (result.x(), result.y())

    cpdef transform_points(self, np.ndarray points, float offset=0):
        cdef np.ndarray r_value = np.zeros_like(points,dtype=np.float)
        for i in range(points.shape[0]):
            elem = points[i]
            r_value[i] = self.transform_point_to_location(elem[0], elem[1], offset)

        return r_value

    cpdef debugprint(self):
        self.transformer.get_robot().print_robot_data_for_debug()

    cpdef get_camera_angle(self):
        return self.transformer.get_camera_angle()

    cpdef float ray_motor_distance(self, object point):
        return self.transformer.get_ray_motor_distance(Vector2d(<double>point[0], <double>point[1])) * 1000

    cpdef list convex_hull(self, object image_points):
        cdef MatrixXf im_points = MatrixXf(2, len(image_points))
        for i in range(len(image_points)):
            im_points.col(i).insert(Vector2f(float(image_points[i][0]), float(image_points[i][1])))
        cdef vector[bool] result = self.transformer.convex_hull(im_points)
        print result
        return [b for b in result]

    property robot:
        def __get__(self):
            cdef Robot robot = Robot(True)
            robot.robot = deconstify_robot(ref(self.transformer.get_robot()))
            return robot
