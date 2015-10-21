#!/usr/bin/env python
#-*- coding:utf-8 -*-

import numpy

from glrobot.scenegraph import VertexBufferObject

class Plane(VertexBufferObject):
    def __init__(self, texture=None):
        vertices = numpy.asarray([
            [-1, 0, 1], [1, 0, 1], [-1, 0, -1],
            [-1, 0,-1], [1, 0, 1], [ 1, 0, -1]
        ], dtype=numpy.float32) / 2
        
        texcoords = numpy.asarray([
            [0, 1], [1, 1], [0, 0],
            [0, 0], [1, 1], [1, 0]
        ], dtype=numpy.float32)
        
        normals = numpy.asarray([(0, 1, 0)] * 6, dtype=numpy.float32)
        
        super(Plane, self).__init__()
        self.update_normals(normals)
        self.update_vertices(vertices)
        self.update_texcoords(texcoords)
        self.texture = texture
        
