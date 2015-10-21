from direct.directbase import DirectStart
from panda3d.ode import OdeWorld, OdeSimpleSpace, OdeJointGroup
from panda3d.ode import OdeBody, OdeMass, OdeBoxGeom, OdePlaneGeom
from panda3d.core import BitMask32, CardMaker, Vec4, Quat
from random import randint, random
from direct.directbase import DirectStart
from direct.directtools.DirectGeometry import LineNodePath
from panda3d.core import *
from panda3d.ode import *

# Setup our physics world
world = OdeWorld()
world.setGravity(0, 0, -9.81)
 
# The surface table is needed for autoCollide
world.initSurfaceTable(1)
world.setSurfaceEntry(0, 0, 150, 0.0, 9.1, 0.9, 0.00001, 0.0, 0.002)
 
# Create a space and add a contactgroup to it to add the contact joints
space = OdeSimpleSpace()
space.setAutoCollideWorld(world)
contactgroup = OdeJointGroup()
space.setAutoCollideJointGroup(contactgroup)
 
# Load the box
box = loader.loadModel("box")
box.setScale(4, 4, 1)
# Make sure its center is at 0, 0, 0 like OdeBoxGeom
box.setPos(1, 1, 1)
box.flattenLight() # Apply transform
box.setTextureOff()




# Add a random amount of boxes
boxes = []

# Setup the geometry
boxNP = box.copyTo(render)
boxNP.setPos(randint(-10, 10), randint(-10, 10), 10 + random())
boxNP.setColor(random(), random(), random(), 1)
boxNP.setHpr(0, 45, 0)

# Create the body and set the mass
boxBody = OdeBody(world)
M = OdeMass()
M.setBox(20, 1, 1, 1)
boxBody.setMass(M)
boxBody.setPosition(boxNP.getPos(render))
boxBody.setQuaternion(boxNP.getQuat(render))
# Create a BoxGeom
boxGeom = OdeBoxGeom(space, 4, 4, 1)
boxGeom.setCollideBits(BitMask32(0x00000002))
boxGeom.setCategoryBits(BitMask32(0x00000001))
boxGeom.setBody(boxBody)
boxes.append((boxNP, boxBody))


boxNP2 = box.copyTo(render)
boxNP2.reparentTo(boxNP)
boxNP2.setPos(0.5, 0.5, 0)
boxNP2.setScale(0.1, 0.1, 4)

boxBody2 = OdeBody(world)
M2 = OdeMass()
M2.setBox(150, 0.1, 0.1, 2)
boxBody2.setMass(M2)

smileyJoint = OdeBallJoint(world)
smileyJoint.attach(boxBody2, boxBody) # Attach it to the environment
smileyJoint.setAnchor(0, 0, 2)


 
# Add a plane to collide with
cm = CardMaker("ground")
cm.setFrame(-20, 20, -20, 20)
ground = render.attachNewNode(cm.generate())
ground.setPos(0, 0, 0); ground.lookAt(0, 0, -1)
groundGeom = OdePlaneGeom(space, Vec4(0, 0, 1, 0))
groundGeom.setCollideBits(BitMask32(0x00000001))
groundGeom.setCategoryBits(BitMask32(0x00000002))
 
# Set the camera position
base.disableMouse()
base.camera.setPos(40, 40, 20)
base.camera.lookAt(0, 0, 0)
 
# The task for our simulation
def simulationTask(task):
  space.autoCollide() # Setup the contact joints
  # Step the simulation and set the new positions
  world.quickStep(globalClock.getDt())
  for np, body in boxes:
    np.setPosQuat(render, body.getPosition(), Quat(body.getQuaternion()))
  contactgroup.empty() # Clear the contact joints
  return task.cont
 
# Wait a split second, then start the simulation  
taskMgr.doMethodLater(0.5, simulationTask, "Physics Simulation")
 
run()