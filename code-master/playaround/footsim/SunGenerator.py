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

# Orbital Imports
from ObjectGenerator import ObjectGenerator


class SunGenerator(ObjectGenerator):
    
    def __init__(self):
        ObjectGenerator.__init__(self)
        pass

    def createNewSun(self, radius, phi_range, thetha_range, vertexcolour = None, transparency = 1, texturename = None, texturealpha = 1):
        geomnode = ObjectGenerator.createNewSphere(self, radius, phi_range, thetha_range, vertexcolour , transparency )
        return Sun(geomnode, texturename, texturealpha)

class Sun(NodePath):
    
    def __init__(self, geomnode, texturename, texturealpha):

        NodePath.__init__(self, "Sun")
        NodePath(geomnode).reparentTo(self)
        
        self.material = Material()
        if(texturename != None):
            self.loadTexture(texturename, texturealpha)


        #self.initLight()
        # self.initPhysics()
        # self.initForceNode()


    def initPhysics(self):
        """
        Initalize Physics (Attach speed and rotation force)
        """
        base.physicsMgr.attachPhysicalNode(self.actorNode)

        cs = CollisionSphere(0, 0, 0, 10)
        cnodePath = self.attachNewNode(CollisionNode('cnode'))
        cnodePath.node().addSolid(cs)
        cnodePath.show()


    def initForceNode(self):
        """
        Initalize Force (ForceNode)
        """
        self.forceNodeContainer = NodePath("AbstractShip - ForceNodeContainer")
        self.forceNodeContainer.reparentTo(self)
        self.forceNodeMotion = ForceNode('AbstractShip - Force Node - Motion ')
        NodePath(self.forceNodeMotion).reparentTo(self.forceNodeContainer)
        
        
    def initLight(self):
        slight = PointLight('slight')
        slight.setColor(VBase4(1, 1, 1, 1))
        slight.setAttenuation(Point3(0, 0, 0.001))
        lens = PerspectiveLens()
        slight.setLens(lens)
        self.slnp = self.attachNewNode(slight)
        self.slnp.setPos(0, 0, 1)
        render.setLight(self.slnp)
  
  
    def loadTexture(self, texturename, texturealpha):
        txt = loader.loadTexture(texturename)
        txt.setWrapU(Texture.WMRepeat)
        txt.setWrapV(Texture.WMRepeat)
        txt.setMagfilter(Texture.FTNearest)
        txt.setMinfilter(Texture.FTNearest)
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MBlend)
        ts.setColor(Vec4(1, 1, 1, texturealpha))
        self.setTexture(ts, txt)
    ###########################
    ### Material Properties ###
    ###########################
    
    def setShininess(self, shininess):
        self.material.setShininess(shininess)
        
    def setAmbient(self, ambient):
        self.material.setAmbient(ambient)
        
    def setEmission(self, emission):
        self.material.setEmission(emission)
        
    def setSpecular(self, specular):
        self.material.setSpecular(specular)
        
    def setDiffuse(self, diffuse):
        self.material.setDiffuse(diffuse)
        
    def applyMaterial(self):
        self.setMaterial(self.material)

    
    #####################
    ### Movement Part ###
    #####################

      
    def startRotation(self, speed):
        self.rotate_v = speed
        taskMgr.add(self.rotate, 'Task Name')    
            
    def rotate(self, task):
        self.setH(self.getH() + self.rotate_v * globalClock.getDt())
        return task.cont
    
    def startRotationAround(self, speed, radius, center = None, phaseShift = 0):
        self.delta_rotateAround = speed
        self.radius = radius
        self.current_rotateAround = phaseShift
        self.center = center
        taskMgr.add(self.rotateAround, 'Task Name')    
            
    def rotateAround(self, task):
        self.current_rotateAround += self.delta_rotateAround * globalClock.getDt()
        
        if(self.center != None):
            y = math.sin(self.current_rotateAround) * self.radius + self.center.getX()
            x = math.cos(self.current_rotateAround) * self.radius + self.center.getY()
        else:
            y = math.sin(self.current_rotateAround) * self.radius
            x = math.cos(self.current_rotateAround) * self.radius         

        self.setPos(x, y, self.getPos().getZ())
        return task.cont
