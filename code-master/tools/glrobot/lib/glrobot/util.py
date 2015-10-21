#!/usr/bin/env python
#-*- coding:utf-8 -*-

from OpenGL.GL import glPushMatrix, glPopMatrix

class __MatrixGuard(object):
    def __enter__(self):
        glPushMatrix()
    
    def __exit__(self, *ignore):
        glPopMatrix()
    
    def __call__(self):
        pass
    
glPreserveMatrix = __MatrixGuard()

