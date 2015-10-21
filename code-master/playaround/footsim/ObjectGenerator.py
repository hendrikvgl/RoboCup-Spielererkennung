# General Imports
import time
import random 
import numpy as np
import math

# Panda Imports
from panda3d.core import Texture, GeomNode
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTrifans, GeomTristrips, GeomVertexWriter, GeomTriangles
from panda3d.core import Vec3, Vec4, Point3
from pandac.PandaModules import NodePath
from pandac.PandaModules import *
from direct.gui.DirectGui import *



class ObjectGenerator():
    '''
    This Class creates a Generator to Generate different Geoms with different Parameters
    '''
    def __init__(self):
        pass

    def createNewSphere(self, radius, height, width, vertexcolour = None, transparency = 1):
        ''' 
        Note that the first and the last node of the Thetha_Range should be 0 and 180 Degrees 
        because this will be just one time added to verticies
        '''
        #Format
        format = GeomVertexFormat.getV3n3cpt2()
        #VertexData
        vdata = GeomVertexData('name', format, Geom.UHStatic)


        ##VertexWriter
        vertex      = GeomVertexWriter(vdata, 'vertex')
        normal      = GeomVertexWriter(vdata, 'normal')
        color       = GeomVertexWriter(vdata, 'color')
        texcoord    = GeomVertexWriter(vdata, 'texcoord')
        
        if (vertexcolour == None):
            vertexcolour = [0.5, 0.5, 0.5]
        
        counter = 0
        ### Create the Skeleton of the Sphere
        for j in range(width):
            for i in range(height):
                if (i == 0):
                    vect = self.sphereToKartesian(radius, 0, 0)
                    vertex.addData3f(vect[0],vect[1],vect[2])
                    normal.addData3f(vect[0],vect[1],vect[2])
                    color.addData4f(vertexcolour[0],vertexcolour[1],vertexcolour[2],transparency)
                    texcoord.addData2f(1-(float(j)/(width)), (float(i)/(height)))                   
                elif (i == height-1):
                    vect = self.sphereToKartesian(radius, 0, 180)
                    vertex.addData3f(vect[0],vect[1],vect[2])
                    normal.addData3f(vect[0],vect[1],vect[2])
                    color.addData4f(vertexcolour[0],vertexcolour[1],vertexcolour[2],transparency)
                    texcoord.addData2f(1-(float(j)/(width)), (float(i)/(height)))
                else:
                    vect = self.sphereToKartesian(radius, (float(j)/(width-2)) * 360, (float(i)/(height)) * 180)
                    vertex.addData3f(vect[0],vect[1],vect[2])
                    normal.addData3f(vect[0],vect[1],vect[2])
                    texcoord.addData2f(1-(float(j)/(width-2)), (float(i)/(height)))
                    color.addData4f(vertexcolour[0],vertexcolour[1],vertexcolour[2],transparency)
                    counter += 1

        ### Create Geom
        geom = Geom(vdata)
        
        
        ### Create Top Trifans
        prim = self.createTrifans(0,range(1,width+1))
       #geom.addPrimitive(prim)
        
        ### Create Belttristrips
        
        for i in range(0,height-2):
            prim = self.createTristrips(width, width*i)

            geom.addPrimitive(prim)
        

        ### Create Bottom Trifans
        lastpoint = width*height-1
        a = [i-1 for i in range(lastpoint,lastpoint-width,-1)]
        prim = self.createTrifans(lastpoint,a)
        #geom.addPrimitive(prim)
 
        geomnode = GeomNode('gnode')
        geomnode.addGeom(geom)
        
        return geomnode


    def createTetraeder(self, iterations):
        ''' 
        Note that the first and the last node of the Thetha_Range should be 0 and 180 Degrees 
        because this will be just one time added to verticies
        '''
        #Format
        format = GeomVertexFormat.getV3n3cpt2()
        #VertexData
        vdata = GeomVertexData('name', format, Geom.UHDynamic)


        ##VertexWriter
        vertex      = GeomVertexWriter(vdata, 'vertex')
        normal      = GeomVertexWriter(vdata, 'normal')
        color       = GeomVertexWriter(vdata, 'color')
        texcoord    = GeomVertexWriter(vdata, 'texcoord')
        
        
        vertex.addData3f(0,1.434,-0.507)
        vertex.addData3f(-1.242,-0.717,-0.507)
        vertex.addData3f(1.242,-0.717,-0.507)
        vertex.addData3f(0,0,1.521)
        
        color.addData4f(1,1,1,1)
        color.addData4f(1,1,1,1)
        color.addData4f(1,1,1,1)
        color.addData4f(1,1,1,1)

        normal.addData3f(0,1.434,-0.507)
        normal.addData3f(-1.242,-0.717,-0.507)
        normal.addData3f(1.242,-0.717,-0.507)
        normal.addData3f(0,0,1.521)

        ### Create Geom
        geom = Geom(vdata)
        ### Create Primitives
        prim = GeomTriangles(Geom.UHStatic)
        prim.addVertices(0, 1, 2)
        prim.addVertices(0, 1, 3)
        prim.addVertices(1, 2, 3)
        prim.addVertices(2, 0, 3)
        prim.closePrimitive()

        geom.addPrimitive(prim)
        
        node = GeomNode('gnode')
        node.addGeom(geom)
        
        return node




    def createTrifans(self, basepoint, pointrange):
        prim = GeomTrifans(Geom.UHStatic)
        prim.addVertex(basepoint)
        for i in pointrange:
            prim.addVertex(i)
        prim.addVertex(pointrange[0])
        prim.closePrimitive()
        return prim

    def createTristrips(self, pointCount, startPoint):
        prim = GeomTristrips(Geom.UHStatic)
        for i in xrange(pointCount):
            prim.addVertex(i+startPoint)
            prim.addVertex(i+startPoint+pointCount)         
        prim.closePrimitive() 
        return prim
    
############################
#### Mathematic Helpers ####
############################   


    def random(self, fr, to):
        g = random.random()*(to-fr)+fr
        return g 
    
    def degreeToRad(self, degree):
        return (degree/360.0)*2*np.pi

    def sphereToKartesian(self, r, phi, theta):
        phi = self.degreeToRad(phi)
        theta = self.degreeToRad(theta)
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi) 
        z = r * np.cos(theta)
        return [x,y,z]
