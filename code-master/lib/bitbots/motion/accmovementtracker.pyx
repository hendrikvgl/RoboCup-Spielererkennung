#-*- coding:utf-8 -*-
__author__ = 'Sören Nykamp'

cdef class AccMovementTracker(object):

    def __init__(self):

        self.movement = PyDataVector(0.0, 0.0, 0.0)
        self.start_this_period = time.time()
        self.start_last_period = 0.0
        self.last_asked = 0.0
        self.last_input = time.time()
        self.movement_last_period = PyDataVector(0.0, 0.0, 0.0)
        self.velo = PyDataVector(0.0, 0.0, 0.0)


    cdef clear_to_zero(self):

        self.start_last_period = self.start_this_period
        self.start_this_period = time.time()
        self.movement_last_period = self.movement
        self.movement.set(0.0, 0.0, 0.0)

        return self.movement_last_period

    cdef get_actual_vector(self):
        self.last_asked = time.time()

        return self.movement


    cdef apply_acceleration(self, float x, float y, float z, object input_time):
        """
        x,y are accellation in front(x) and side(y) direction
        +x move to front
        -x move to back
        +y
        -y
        z is the rotation (absolute)
        x,y are between -511 and 512 now forces in N

        """
        #input_time = time.time()
        t = input_time - self.last_input
        self.last_input = input_time

        length = sqrt(x**2 + y**2)

        x_rad = length * sin(z)
        y_rad = length * cos(z)

        x_velo = (x_rad) * t
        y_velo = (y_rad) * t

        x_old = self.velo.x
        y_old = self.velo.y
        x_dist = 0.5 * (x) * t * t + x_old * t
        y_dist = 0.5 * (y) * t * t + y_old * t
        self.velo = self.velo + [x_velo, y_velo, 0.0]
        print "x: %s, y: %s, z: %s" % (x, y, z)
        print "x_dist: %s, y_dist: %s" % (x_dist, y_dist)
        print "Velocity: %s" % self.velo
        self.movement = self.movement + PyDataVector(x_dist, y_dist, 0.0)
        print "Movement: %s" % self.movement
