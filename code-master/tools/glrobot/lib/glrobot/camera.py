#!/usr/bin/env python
#-*- coding:utf-8 -*-

import math

from OpenGL.GL import glMatrixMode, glRotate, glTranslate, glLoadIdentity
from OpenGL.GL import GL_MODELVIEW

from glrobot.scenegraph import Node

class Camera(Node):
    def __init__(self, position = (0, 0, 0), yaw = 0, pitch = 0):
        super(Camera, self).__init__()

        self.speed = 5
        self.position = list(position)
        self.pitch = pitch
        self.yaw = yaw

    def move(self, dx, dy, dz, dt):
        speed = self.speed * dt * 0.1
        ax, ay = math.radians(self.pitch), math.radians(self.yaw)
        self.position[0] -= (math.sin(ay)*math.cos(ax)*dz - math.cos(ay)*dx)*speed
        self.position[1] += (math.sin(ax)*dz + dy)*speed
        self.position[2] -= (-math.cos(ay)*math.cos(ax)*dz - math.sin(ay)*dx)*speed

    def rotate(self, yaw, pitch):
        self.yaw += yaw
        self.pitch = min(90, max(-90, self.pitch + pitch))

    def render(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glRotate(self.pitch, 1, 0, 0)
        glRotate(self.yaw,   0, 1, 0)

        x, y, z = self.position
        glTranslate(-x, -y, -z)

class FPSCamera(Camera):
    def __init__(self, *args, **kwargs):
        super(FPSCamera, self).__init__(*args, **kwargs)
        self.mouse = None

    def update(self, keys, dt):
        dx, dy, dz = 0, 0, 0
        ry, rx= 0, 0

        if "a" in keys:
            dx -= 1
        if "d" in keys:
            dx += 1
        if "w" in keys:
            dz -= 1
        if "s" in keys:
            dz += 1
        if "q" in keys:
            dy -= 1
        if "e" in keys:
            dy += 1

        if "h" in keys:
            rx -= 1
        if "l" in keys:
            rx += 1
        if "j" in keys:
            ry += 1
        if "k" in keys:
            ry -= 1

        self.move(dx, dy, dz, dt)
        self.rotate(rx, ry)

    def handle_mouse_event(self, down, x, y):
        self.mouse = [x, y] if down else None

    def handle_mouse_motion_event(self, x, y):
        if self.mouse is None:
            return

        f = 0.3
        last_x, last_y = self.mouse
        self.rotate((x-last_x)*f, (y-last_y)*f)
        self.mouse = [x, y]

