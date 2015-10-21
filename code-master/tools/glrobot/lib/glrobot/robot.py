#!/usr/bin/env python
#-*- coding:utf-8 -*-

from OpenGL.GL import *
import numpy as np

import glrobot.loader
from glrobot.scenegraph import *
from glrobot.util import glPreserveMatrix

from bitbots.robot.pypose import PyPose as Pose
from bitbots.util import find_resource
import bitbots.robot.kinematics as kinematics
from bitbots.robot.kinematics import rfoot, lfoot

# The reimplementation of the kinematic framework had an change of axis as consequense
# To maintain compatibility to this tool, we need to adjust these values manually
# First version is to convert the old coordinate axis to the new, the second one
# is the inversion, the conversion from the old axis to the new.
# In addition, the framework changed to mm instet of m, so you'll find some '/1000.0'
# expressions after accessing the position or centre of gravity of the robot
axis_conversion = np.array(([0, 0, 1],[1, 0, 0],[0, 1, 0]))
axis_conversion = np.array(([0, 1, 0],[0, 0, 1],[1, 0, 0]))
axis_conversion_4 = np.array(([0, 1, 0, 0],[0, 0, 1, 0],[1, 0, 0, 0], [0, 0, 0, 0]))

def find(what):
    return find_resource(what, base="glrobot/")

class Robot(Group):
    def __init__(self):
        super(Robot, self).__init__()

        self.xray = False
        self.blend = False

        self.alpha_functions = []
        self.color_plastique = [0.7, 0.7, 0.7, 1]
        self.color_metal = [1, 1, 1, 1]
        self.color_servo = [.2, .2, .2, 1]
        self.color_eye = [0.05, 0.05, 0.05, 1]
        self.color_head_led = [.5, 1, .5, 1]
        self.color_iris = [.5, .5, 1, 1]

    def set_alpha(self, alpha=1):
        self.blend = alpha < 0.99
        for func in self.alpha_functions:
            func(alpha)

    def load(self):
        def load(name, color=self.color_plastique):
            filename = find("gl/%s.obj" % name)
            obj =glrobot.loader.load_object_from_obj(filename)
            obj.set_color(*color)
            self.alpha_functions.append(obj.set_alpha)
            return obj

        # Der Nacken
        self.neck = self.make(Group)
        self.neck.set_position(0, 0.051, 0)
        self.neck.add(load("neck", self.color_metal))

        # Kopf mit Augen und LEDs
        self.head = self.neck.make(Group)
        self.head.rotation_axis.x = -1
        self.head.rotation_offset.x = -45

        self.head.add(load("head"))
        self.head.add(load("head-led", self.color_head_led))
        self.head.add(load("eyes", self.color_eye))
        self.head.add(load("eyes-iris", self.color_iris))

        # Den Körper des Roboters
        self.add(load("body"))

        # Linker Arm
        self.l_shoulder_pitch = self.make(Group)
        self.l_shoulder_pitch.set_position(0.082, 0, 0)
        self.l_shoulder_pitch.add(load("shoulder-l", self.color_metal))

        self.l_shoulder_roll = self.l_shoulder_pitch.make(Group)
        self.l_shoulder_roll.set_position(0, -0.016, 0)
        self.l_shoulder_roll.rotation_axis.z = -1
        self.l_shoulder_roll.rotation_offset.z = -45
        self.l_shoulder_roll.add(load("arm-upper-shape-l"))
        self.l_shoulder_roll.add(load("arm-upper-servo-l", self.color_servo))

        self.l_elbow = self.l_shoulder_roll.make(Group)
        self.l_elbow.set_position(0, -0.06, 0.016)
        self.l_elbow.rotation_offset.x = -90
        self.l_elbow.add(load("arm-lower-shape-l"))
        self.l_elbow.add(load("arm-lower-metal-l", self.color_metal))

        # Rechter Arm
        self.r_shoulder_pitch = self.make(Group)
        self.r_shoulder_pitch.set_position(-0.082, 0, 0)
        self.r_shoulder_pitch.rotation_axis.x = -1
        self.r_shoulder_pitch.add(load("shoulder-r", self.color_metal))

        self.r_shoulder_roll = self.r_shoulder_pitch.make(Group)
        self.r_shoulder_roll.set_position(0, -0.016, 0)
        self.r_shoulder_roll.rotation_axis.z = -1
        self.r_shoulder_roll.rotation_offset.z = 45
        self.r_shoulder_roll.add(load("arm-upper-shape-r"))
        self.r_shoulder_roll.add(load("arm-upper-servo-r", self.color_servo))

        self.r_elbow = self.r_shoulder_roll.make(Group)
        self.r_elbow.set_position(0, -0.06, 0.016)
        self.r_elbow.rotation_axis.x = -1
        self.r_elbow.rotation_offset.x = 90
        self.r_elbow.add(load("arm-lower-shape-r"))
        self.r_elbow.add(load("arm-lower-metal-r", self.color_metal))

        # Linkes Bein
        self.l_hip_yaw = self.make(Group)
        self.l_hip_yaw.set_position(0.037, -0.1222, -0.005)
        self.l_hip_yaw.rotation_axis.y = -1
        self.l_hip_yaw.add(load("leg-hip-y-l", self.color_metal))

        self.l_hip_roll = self.l_hip_yaw.make(Group)
        self.l_hip_roll.rotation_axis.z = -1
        self.l_hip_roll.add(load("leg-hip-l", self.color_servo))

        self.l_hip_pitch = self.l_hip_roll.make(Group)
        self.l_hip_pitch.rotation_axis.x = -1
        self.l_hip_pitch.add(load("leg-upper-shape-l"))
        self.l_hip_pitch.add(load("leg-upper-servo-l", self.color_servo))

        self.l_knee = self.l_hip_pitch.make(Group)
        self.l_knee.set_position(0, -0.093, 0)
        self.l_knee.rotation_axis.x = -1
        self.l_knee.add(load("leg-lower-shape-l"))

        self.l_ankle_pitch = self.l_knee.make(Group)
        self.l_ankle_pitch.set_position(0, -0.093, 0)
        self.l_ankle_pitch.add(load("ankle-servo-l", self.color_servo))

        self.l_ankle_roll = self.l_ankle_pitch.make(Group)
        self.l_ankle_roll.add(load("foot-l"))
        self.l_ankle_roll.add(load("foot-metal-l", self.color_metal))

        # Rechtes Bein
        self.r_hip_yaw = self.make(Group)
        self.r_hip_yaw.set_position(-0.037, -0.1222, -0.005)
        self.r_hip_yaw.rotation_axis.y = -1
        self.r_hip_yaw.add(load("leg-hip-y-r", self.color_metal))

        self.r_hip_roll = self.r_hip_yaw.make(Group)
        self.r_hip_roll.rotation_axis.z = -1
        self.r_hip_roll.add(load("leg-hip-r", self.color_servo))

        self.r_hip_pitch = self.r_hip_roll.make(Group)
        self.r_hip_pitch.add(load("leg-upper-shape-r"))
        self.r_hip_pitch.add(load("leg-upper-servo-r", self.color_servo))

        self.r_knee = self.r_hip_pitch.make(Group)
        self.r_knee.set_position(0, -0.093, 0)
        self.r_knee.add(load("leg-lower-shape-r"))

        self.r_ankle_pitch = self.r_knee.make(Group)
        self.r_ankle_pitch.set_position(0, -0.093, 0)
        self.r_ankle_pitch.rotation_axis.x = -1
        self.r_ankle_pitch.add(load("ankle-servo-r", self.color_servo))

        self.r_ankle_roll = self.r_ankle_pitch.make(Group)
        self.r_ankle_roll.add(load("foot-r"))
        self.r_ankle_roll.add(load("foot-metal-r", self.color_metal))

    def set_pose(self, pose, which='position'):
        get = lambda name: getattr(getattr(pose, name), which)

        self.neck.rotation.y = get("head_pan")
        self.head.rotation.x = get("head_tilt")

        self.l_shoulder_pitch.rotation.x = get("l_shoulder_pitch")
        self.l_shoulder_roll.rotation.z = get("l_shoulder_roll")
        self.l_elbow.rotation.x = get("l_elbow")

        self.r_shoulder_pitch.rotation.x = get("r_shoulder_pitch")
        self.r_shoulder_roll.rotation.z = get("r_shoulder_roll")
        self.r_elbow.rotation.x = get("r_elbow")

        self.l_hip_yaw.rotation.y = get("l_hip_yaw")
        self.l_hip_roll.rotation.z = get("l_hip_roll")
        self.l_hip_pitch.rotation.x = get("l_hip_pitch")
        self.l_knee.rotation.x = get("l_knee")
        self.l_ankle_pitch.rotation.x = get("l_ankle_pitch")
        self.l_ankle_roll.rotation.z = get("l_ankle_roll")

        self.r_hip_yaw.rotation.y = get("r_hip_yaw")
        self.r_hip_roll.rotation.z = get("r_hip_roll")
        self.r_hip_pitch.rotation.x = get("r_hip_pitch")
        self.r_knee.rotation.x = get("r_knee")
        self.r_ankle_pitch.rotation.x = get("r_ankle_pitch")
        self.r_ankle_roll.rotation.z = get("r_ankle_roll")

    def render(self):
        if self.blend:
            glEnable(GL_BLEND)
            if self.xray:
                glDepthMask(GL_FALSE)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE )
            else:
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            super(Robot, self).render()

            glDepthMask(GL_TRUE)
            glDisable(GL_BLEND)
        else:
            # direkt zeichnen
            super(Robot, self).render()

class Bone(MatrixNode):
    def __init__(self, sphere, line):
        gr = Group()
        super(Bone, self).__init__(gr)
        gr.add(sphere)

        self.line = MatrixNode(line)
        gr.add(self.line)

class Skeleton(Group):
    def __init__(self, sphere, bone):
        super(Skeleton, self).__init__()

        self.robot = kinematics.Robot()
        self.robot.update(Pose())

        self.sphere = sphere
        self.bone = bone

    def update(self, pose):
        self.robot.update(pose)

    def get_alignment_auto(self):
        leg_l = np.dot(axis_conversion_4, self.robot.get_joint_by_id(lfoot()).get_chain_matrix())
        leg_l_inv = np.dot(axis_conversion_4, self.robot.get_joint_by_id(lfoot()).get_chain_matrix(inverse=True))

        leg_r = np.dot(axis_conversion_4, self.robot.get_joint_by_id(rfoot()).get_chain_matrix())
        leg_r_inv = np.dot(axis_conversion_4, self.robot.get_joint_by_id(rfoot()).get_chain_matrix(inverse=True))

        l_to_r = numpy.dot(numpy.dot(numpy.dot(leg_l_inv, leg_r), (0, 0, 0, 1)), (0, 1, 0, 0))
        r_to_l = numpy.dot(numpy.dot(numpy.dot(leg_r_inv, leg_l), (0, 0, 0, 1)), (0, 1, 0, 0))

        left = l_to_r > 0 > r_to_l
        result = leg_l_inv if left else leg_r_inv

        x_offset = numpy.dot(numpy.dot(result, (0, 0, 0, 1)), (1, 0, 0, 0))
        result[0,3] -= x_offset
        return result

    def get_alignment_left_leg(self):
        return np.dot(axis_conversion_4, self.robot.get_joint_by_id(lfoot()).get_chain_matrix(inverse=True))

    def get_alignment_right_leg(self):
        return np.dot(axis_conversion_4, self.robot.get_joint_by_id(rfoot()).get_chain_matrix(inverse=True))

    def get_alignment_none(self):
        matrix = numpy.eye(4, dtype=numpy.float32)
        matrix[1,3] = 0.346131
        return matrix

    def render_chain(self, chain):
        sphere = Group(self.sphere)
        bone = MatrixNode(self.bone)

        prev = None
        for joint in chain:
            position = np.dot(axis_conversion, joint.get_endpoint() / 1000.0)
            sphere.set_position(*position)
            sphere.render()

            #cog = joint.get_centre_of_gravity()
            #sphere.set_position(*cog)
            #sphere.render()

            if prev is not None:
                position = numpy.array(position, dtype=numpy.float32)
                bone.set_matrix_from_axis(position - prev, prev)
                bone.render()

            prev = position

            pos = np.dot(axis_conversion, joint.get_centre_of_gravity() / 1000.0)
            cog = Group(self.sphere)
            cog.set_position(*pos)
            cog.render()

    def render(self):
        with glPreserveMatrix:
            self.transform()
            self.render_chain(self.robot.get_head_chain())
            self.render_chain(self.robot.get_l_leg_chain())
            self.render_chain(self.robot.get_r_leg_chain())
            self.render_chain(self.robot.get_l_arm_chain())
            self.render_chain(self.robot.get_r_arm_chain())

            pos = np.dot(axis_conversion, self.robot.get_centre_of_gravity()[0:3] / 1000.0)
            cog = Group(self.sphere)
            cog.set_position(*pos)
            cog.render()

