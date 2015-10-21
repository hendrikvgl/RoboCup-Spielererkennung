#!/usr/bin/env python
#-*- coding:utf-8 -*-

from glrobot.scenegraph import Texture, VertexBufferObject

import gtk
import numpy

def load_texture_from_file(name):
    pixbuf = gtk.gdk.pixbuf_new_from_file(name)
    tex = Texture()
    tex.update(pixbuf.get_width(), pixbuf.get_height(), pixbuf.get_pixels())
    return tex

def load_object_from_obj(name):
    with open(name) as fp:
        lines = [l.strip() for l in fp]
    
    indices = []
    vertices = []
    texcoords = []
    
    for line in lines:
        if line.startswith("v "):
            vertices.append(map(float, line[2:].split()))
        
        if line.startswith("vt "):
            texcoords.append(map(float, line[3:].split()))
        
        if line.startswith("f "):
            points = [map(int, p.split("/")) for p in line[2:].split()]
            for idx in xrange(2, len(points)):
                Va = points[0][0] - 1
                Vb = points[idx-1][0] - 1
                Vc = points[idx][0] - 1
                
                indices.extend((Va, Vb, Vc))
    
    vertices = numpy.asarray(vertices, dtype=numpy.float32).reshape((-1, 3))[indices]
    normals = numpy.empty(vertices.shape, dtype=numpy.float32)
    for idx, (a, b, c) in enumerate(vertices.reshape((-1, 3, 3))):
        no = numpy.cross(c-b, a-b)
        normals[3*idx+0] = no
        normals[3*idx+1] = no
        normals[3*idx+2] = no
    
    obj = VertexBufferObject()
    obj.update_vertices(vertices)
    obj.update_normals(normals)
    return obj
