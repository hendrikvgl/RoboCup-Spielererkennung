# General Imports
import gevent
import random
from evdev import InputDevice, categorize, ecodes, list_devices, RelEvent, KeyEvent, SynEvent, AbsEvent
from evdev._ecodes import FF_RUMBLE
from evdev.ecodes import REL, ABS
import numpy as np
import numpy.linalg as la



# Panda Imports
from multiprocessing.dummy import current_process
import math
from panda3d.core import *
from pandac.PandaModules import AngularEulerIntegrator
from pandac.PandaModules import ForceNode
from pandac.PandaModules import LinearVectorForce
from pandac.PandaModules import ActorNode
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from MotorControlQLearner import RobotFootQLearner
from ObjectGenerator import ObjectGenerator
from SunGenerator import SunGenerator
from objects.GeomGenerator import GeomGenerator
from direct.gui.OnscreenText import OnscreenText


def create_plane():
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


        vertex.addData3f(-50, -50, 0)
        vertex.addData3f(50, -50, 0)
        vertex.addData3f(-50, 50, 0)
        vertex.addData3f(50, 50, 0)

        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)
        color.addData4f(1, 1, 1, 1)

        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)
        normal.addData3f(0, 0, 1)

        ### Create Geom
        geom = Geom(vdata)
        ### Create Primitives
        prim = GeomTriangles(Geom.UHStatic)
        prim.addVertices(0, 1, 2)
        prim.addVertices(2, 1, 3)
        prim.closePrimitive()

        geom.addPrimitive(prim)

        node = GeomNode('gnode')
        node.addGeom(geom)

        return node


def sign(p1, p2, p3):
  return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def PointInAABB(pt, c1, c2):
  return c2[0] <= pt[0] <= c1[0] and \
         c2[1] <= pt[1] <= c1[1]

def PointInTriangle(pt, v1, v2, v3):
  b1 = sign(pt, v1, v2) <= 0
  b2 = sign(pt, v2, v3) <= 0
  b3 = sign(pt, v3, v1) <= 0

  return ((b1 == b2) and (b2 == b3)) and \
         PointInAABB(pt, map(max, v1, v2, v3), map(min, v1, v2, v3))



class Piece(NodePath):

    def __init__(self, name, scene_anchor, geom_result):
        self.content = NodePath("content")
        NodePath.__init__(self, self.content)
        self.setName(name)
        self.scene_anchor = scene_anchor

        self.volume = geom_result.volume
        self.density = 1
        x, y, z = geom_result.center
        assert x == 0 and y == 0 and z == 0, ("Failed", x, y, z)

        # The node that shows the center of mass
        self.com = loader.loadModel('smiley')
        self.com.setName("center_of_mass")
        self.com.reparentTo(self.content)
        self.com.setColor(1, 0, 0)
        self.com.setScale(0.25, 0.25, 0.25)
        self.com.setTransparency(TransparencyAttrib.MNone)

    def get_global_position(self):
        return self.get_pos(self.scene_anchor)

    def overwrite_density(self, density):
        self.density = density

class Foot(Piece):

    def __init__(self, scene_anchor):
        geom_result = GeomGenerator.get_foot_geom()
        Piece.__init__(self, "MotorHorn", scene_anchor, geom_result)

        foot = NodePath(geom_result.geom)
        foot.setPos(0, 0, 0)
        foot.reparentTo(self.content)

class MotorHorn(Piece):

    def __init__(self, scene_anchor):
        geom_result = GeomGenerator.create_box()
        Piece.__init__(self, "MotorHorn", scene_anchor, geom_result)

        self.motor_limits = [-60, 60]
        self.motor_speed = 5
        self.direction = 1

        self.motor_horn = NodePath(geom_result.geom)
        self.motor_horn.setRenderModeWireframe()

        self.motor_horn.setColor(0, 1, 0)
        self.motor_horn.reparentTo(self.content)

    def startRotation(self, speed):
        self.rotate_v = speed
        taskMgr.add(self.rotate, 'Task Name')


    def rotate_delta(self, delta):
        current_p = self.getP()
        next_p = current_p + delta * self.motor_speed * globalClock.getDt()
        if self.motor_limits[0] <= next_p <= self.motor_limits[1]:
            self.setP(next_p)

    def rotate(self, task):
        current_p = self.getP()
        next_p = current_p + self.direction * self.motor_speed * globalClock.getDt()
        if self.motor_limits[0] <= next_p <= self.motor_limits[1]:
            self.setP(next_p)
        else:
            self.direction *= -1

        return task.cont

class MotorBase(Piece):

    def __init__(self, scene_anchor):
        geom_result = GeomGenerator.create_box()
        Piece.__init__(self, "MotorBase", scene_anchor, geom_result)

        self.motor_block = NodePath(geom_result.geom)
        self.motor_block.setRenderModeWireframe()

        self.motor_block.reparentTo(self.content)
        self.motor_block.setPos(0, 0, 0)
        self.motor_block.setColor(1, 0, 0, 1)
        self.motor_block.setScale(1, 1, 1)

    def get_motor_block(self):
        return self.motor_block

class MetalConnector(Piece):

    def __init__(self, scene_anchor):
        geom_result = GeomGenerator.create_box()
        Piece.__init__(self, "MetalConnector", scene_anchor, geom_result)

        self.metal_stick = NodePath(geom_result.geom)
        self.metal_stick.setRenderModeWireframe()
        self.metal_stick.reparentTo(self.content)
        self.setPos(0, 0, 2)
        self.setColor(0, 0, 1)
        self.setScale(1, 1, 1)



class Simulation(ShowBase):

    """This class loads our World for testing purposes"""
    def __init__(self):
        ShowBase.__init__(self)
        self.scenery = NodePath('Scenery2_RootNode')

        self.piece_dictionary = {}

        self.total_center_of_mass = loader.loadModel('smiley')
        self.total_center_of_mass.setName("center_of_mass")
        self.total_center_of_mass.reparentTo(self.scenery)
        self.total_center_of_mass.setColor(1, 1, 0)
        self.total_center_of_mass.setScale(0.25, 0.25, 0.25)
        self.total_center_of_mass.setTransparency(TransparencyAttrib.MNone)
        self.center_of_mass_projection = NodePath("com_projection")
        self.center_of_mass_projection.reparentTo(self.scenery)
        NodePath("Dummy").reparentTo(self.center_of_mass_projection)


        self.triangle_force_A = NodePath("triangle_force_A")
        self.triangle_force_A.setPos((-10, -10, 1))
        self.triangle_force_A.reparentTo(self.scenery)
        NodePath("Dummy").reparentTo(self.triangle_force_A)

        self.triangle_force_B = NodePath("triangle_force_B")
        self.triangle_force_B.setPos((10, -10, 1))
        self.triangle_force_B.reparentTo(self.scenery)
        NodePath("Dummy").reparentTo(self.triangle_force_B)

        self.triangle_force_C = NodePath("triangle_force_C")
        self.triangle_force_C.setPos((0, 20, 1))
        self.triangle_force_C.reparentTo(self.scenery)
        NodePath("Dummy").reparentTo(self.triangle_force_C)


        self.generate_environment()
        self.generate_foot_model()

        self.input_device = InputDevice("/dev/input/event14")

        self.textObject = None
        self.force_distribution = None

        self.controller = Controller()

        self.y_axis_input = 0
        self.x_axis_input = 0
        self.rx_axis_input = 0
        self.ry_axis_input = 0

        self.iterations = 0
        self.piece_dictionary["motor_horn_1"].setP(random.randint(-20, 20))
        self.piece_dictionary["motor_horn_2"].setP(random.randint(-20, 20))
        self.piece_dictionary["motor_horn_3"].setP(random.randint(-40, 0))
        self.piece_dictionary["motor_horn_4"].setP(random.randint(-40, 40))


        taskMgr.add(self.monitor, 'Task Name')
        taskMgr.add(self.control, 'Control Task Name')




    def generate_environment(self):
        f = create_plane()
        np = NodePath(f)
        np.reparentTo(self.scenery)
        np.setPos(0,0,-1)

        slight = PointLight('slight')
        slight.setColor(VBase4(1, 1, 1, 1))
        slight.setAttenuation(Point3(0, 0, 0.001))
        lens = PerspectiveLens()
        slight.setLens(lens)
        np = NodePath(slight)
        np.setPos(0, 0, 50)
        render.setLight(np)


        alight = AmbientLight('alight')
        alnp = render.attachNewNode(alight)
        alight.setColor(Vec4(0.2, 0.2, 0.2, 1))
        render.setLight(alnp)
        self.scenery.reparentTo(render)

        base.cam.setPos(0, -60, 60)
        base.cam.lookAt(0, 0, 1)

    def generate_foot_model(self):

        foot = Foot(self.scenery)
        foot.setRenderModeWireframe()
        foot.reparentTo(self.scenery)
        self.piece_dictionary["foot"] = foot

        m = MotorBase(self.scenery)
        m.setPos(0, 0, 2)
        m.reparentTo(foot)
        self.piece_dictionary["motor_base_1"] = m

        mh = MotorHorn(self.scenery)
        mh.setPos(0, 2, 0)
        mh.setH(90)
        mh.overwrite_density(0)
        mh.reparentTo(m)
        #mh.startRotation(10)
        self.piece_dictionary["motor_horn_1"] = mh

        m = MotorBase(self.scenery)
        m.setPos(0, 0, 2)
        m.reparentTo(mh)
        self.piece_dictionary["motor_base_2"] = m

        mh = MotorHorn(self.scenery)
        mh.setPos(0, 0, 0)
        mh.setH(90)
        mh.reparentTo(m)
        mh.overwrite_density(0)
        #mh.startRotation(10)
        self.piece_dictionary["motor_horn_2"] = mh

        ms2 = MetalConnector(self.scenery)
        ms2.reparentTo(mh)
        self.piece_dictionary["metal_connector_8"] = ms2

        for i in range(9, 12):
            ms3 = MetalConnector(self.scenery)
            ms3.reparentTo(ms2)
            self.piece_dictionary["metal_connector_" + str(i)] = ms3
            ms2 = ms3

        ms3 = MetalConnector(self.scenery)
        ms3.reparentTo(ms2)
        ms3.setScale(1, 1, 1)
        ms3.overwrite_density(1250)
        self.piece_dictionary["metal_connector_20"] = ms3

        m = MotorBase(self.scenery)
        m.setPos(0, 0, 2)
        m.reparentTo(ms3)
        self.piece_dictionary["motor_base_3"] = m

        mh = MotorHorn(self.scenery)
        mh.setPos(0, 0, 0)
        mh.reparentTo(m)
        mh.overwrite_density(0)
        #mh.startRotation(10)
        self.piece_dictionary["motor_horn_3"] = mh
        mh.motor_limits = [-40, 0]

        ms2 = MetalConnector(self.scenery)
        ms2.reparentTo(mh)
        self.piece_dictionary["metal_connector_8"] = ms2

        for i in range(12, 16):
            ms3 = MetalConnector(self.scenery)
            ms3.reparentTo(ms2)
            self.piece_dictionary["metal_connector_" + str(i)] = ms3
            ms2 = ms3

        m = MotorBase(self.scenery)
        m.setPos(0, 0, 0)
        m.setH(90)
        m.reparentTo(ms2)
        self.piece_dictionary["motor_base_4"] = m

        mh = MotorHorn(self.scenery)
        mh.setPos(2, 0, 0)
        mh.overwrite_density(0)
        mh.reparentTo(m)
        #mh.startRotation(10)
        self.piece_dictionary["motor_horn_4"] = mh


        ms3 = MetalConnector(self.scenery)
        ms3.reparentTo(mh)
        ms3.setPos(0, 0, 2)
        ms3.setScale(1, 1, 1)
        ms3.overwrite_density(5000)
        self.piece_dictionary["metal_connector_20"] = ms3


    def draw_force_line(self, triangle_point, color, length):
        # Calculate the force on each of the sensors
        segs = LineSegs()
        segs.setThickness(3.0)
        segs.setColor(*color)
        segs.moveTo(0, 0, 0)
        segs.drawTo(0, 0, length)
        h = segs.create()
        triangle_point.getChild(0).remove_node()
        NodePath(h).reparentTo(triangle_point)

    def barycentric_coords(self, vertices, point):
        T = (np.array(vertices[:-1])-vertices[-1]).T
        v = np.dot(la.inv(T), np.array(point)-vertices[-1])
        v.resize(len(vertices))
        v[-1] = 1-v.sum()
        v[0] -= 0.2
        v[1] += 0.8
        v[2] -= 0.2
        return v

    def calculate_pressure(self):
        acc_x = 0
        acc_y = 0
        acc_z = 0
        total_mass = 0
        for key, value in self.piece_dictionary.items():
            object_pos = value.get_pos(self.scenery)
            acc_x += object_pos.get_x() * value.volume * value.density
            acc_y += object_pos.get_y() * value.volume * value.density
            acc_z += object_pos.get_z() * value.volume * value.density
            total_mass += value.volume * value.density
        acc_x /= float(total_mass)
        acc_y /= float(total_mass)
        acc_z /= float(total_mass)
        self.total_center_of_mass.setPos(acc_x, acc_y, acc_z)
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(1, 1, 0)
        segs.moveTo(acc_x, acc_y, acc_z)
        segs.drawTo(acc_x, acc_y, -5)
        h = segs.create()
        self.center_of_mass_projection.getChild(0).remove_node()
        NodePath(h).reparentTo(self.center_of_mass_projection)
        xA, yA, zA = self.triangle_force_A.get_pos(self.scenery)
        xB, yB, zB = self.triangle_force_B.get_pos(self.scenery)
        xC, yC, zC = self.triangle_force_C.get_pos(self.scenery)
        pA = (xA, yA)
        pB = (xB, yB)
        pC = (xC, yC)
        com_xy = (acc_x, acc_y)
        result = self.barycentric_coords([pA, pB, pC], com_xy)
        am, bm, cm = result
        # Calculate the real force
        amt = result[0] * total_mass * 9.81 * acc_z
        bmt = result[1] * total_mass * 9.81 * acc_z
        cmt = result[2] * total_mass * 9.81 * acc_z
        return am, bm, cm, com_xy, pA, pB, pC

    def monitor(self, task):
        am, bm, cm, com_xy, pA, pB, pC = self.calculate_pressure()

        if self.force_distribution is not None:
            self.force_distribution.destroy()
        self.force_distribution = OnscreenText(text="Point A: {}\nPoint B: {}\nPoint C: {}".format(am, bm, cm),
                                               pos=(-1, 0.9), scale = 0.07)

        if False and not PointInTriangle(com_xy, pA, pB, pC):
            self.draw_force_line(self.triangle_force_A, (1, 0, 0), 5)
            self.draw_force_line(self.triangle_force_B, (1, 0, 0), 5)
            self.draw_force_line(self.triangle_force_C, (1, 0, 0), 5)
        else:
            self.draw_force_line(self.triangle_force_A, (0, 1, 0), am*15)
            self.draw_force_line(self.triangle_force_B, (0, 1, 0), bm*15)
            self.draw_force_line(self.triangle_force_C, (0, 1, 0), cm*15)

        return task.cont


    def handle_event(self, inputevent, typedevent):
        if isinstance(typedevent, AbsEvent):
            kc = ABS[typedevent.event.code]
            if kc is 'ABS_Y':
                value = 1*(-5.0*inputevent.value/32767)
                self.y_axis_input = value
            if kc is 'ABS_X':
                value = -1*(-5.0*inputevent.value/32767)
                self.x_axis_input = value

            if kc is 'ABS_RY':
                value = 1*(-5.0*inputevent.value/32767)
                self.ry_axis_input = value
            if kc is 'ABS_RX':
                value = 1*(-5.0*inputevent.value/32767)
                self.rx_axis_input = value

    def control(self, task):
        self.piece_dictionary["motor_horn_1"].rotate_delta(int(self.x_axis_input))
        self.piece_dictionary["motor_horn_2"].rotate_delta(int(self.y_axis_input))
        self.piece_dictionary["motor_horn_3"].rotate_delta(int(self.ry_axis_input))
        self.piece_dictionary["motor_horn_4"].rotate_delta(int(self.rx_axis_input))

        self.iterations += 1

        if self.iterations > 300 and self.controller is not None:
            self.piece_dictionary["motor_horn_1"].setP(random.randint(-20, 20))
            self.piece_dictionary["motor_horn_2"].setP(random.randint(-20, 20))
            self.piece_dictionary["motor_horn_3"].setP(random.randint(-40, 0))
            self.piece_dictionary["motor_horn_4"].setP(random.randint(-40, 40))
            self.iterations = 0

        if self.controller is not None:
            am, bm, cm, com_xy, pA, pB, pC = self.calculate_pressure()
            v1, v2, v3, v4 = self.controller.step_decision(am, bm, cm)

            self.x_axis_input = v1
            self.y_axis_input = v2
            self.rx_axis_input = v3
            self.ry_axis_input = v4
            return task.cont

        inputevent = self.input_device.read_one()
        if inputevent is None:
            return task.cont

        self.handle_event(inputevent,  categorize(inputevent))

        while inputevent is not None:
            inputevent = self.input_device.read_one()
            if inputevent is None:
                return task.cont
            self.handle_event(inputevent,  categorize(inputevent))



        return task.cont



class Controller():


    def __init__(self):


        self.robot_foot_qlearner = None

        self.goal = [0.33, 0.33, 0.33]
        self.last_pressure_measure = None

        self.initial_control_state = (0, 0, 0, 0)


    def distance(self, v1, v2):
        return math.sqrt((v1[0] - v2[0])**2+(v1[1] - v2[1])**2+(v1[2] - v2[2])**2)

    def to_state(self, value):
        fp1, fp2, fp3 = value
        fpq1 = min(max(0, int(fp1 * 20)), 19)
        fpq2 = min(max(0, int(fp2 * 20)), 19)
        fpq3 = min(max(0, int(fp3 * 20)), 19)
        return [fpq1, fpq2, fpq3]

    def step_decision(self, fp1, fp2, fp3):

        if self.robot_foot_qlearner is None:
            state = self.to_state([fp1, fp2, fp3])
            self.robot_foot_qlearner = RobotFootQLearner(state)
            self.last_pressure_measure = fp1, fp2, fp3
            return (0, 0, 0, 0)

        current_distance = self.distance((fp1, fp2, fp3), self.goal)
        former_distance = self.distance(self.last_pressure_measure, self.goal)

        if current_distance < former_distance:
            self.robot_foot_qlearner.perform_q_learning(self.to_state(self.last_pressure_measure), str(self.initial_control_state), 100, self.to_state((fp1, fp2, fp3)))
        elif fp1 < 0 or fp2 < 0 or fp3 < 0:
            self.robot_foot_qlearner.perform_q_learning(self.to_state(self.last_pressure_measure), str(self.initial_control_state), -10, self.to_state((fp1, fp2, fp3)))
        else:
            self.robot_foot_qlearner.perform_q_learning(self.to_state(self.last_pressure_measure), str(self.initial_control_state), 0, self.to_state((fp1, fp2, fp3)))


        self.last_pressure_measure = fp1, fp2, fp3
        next_action = self.robot_foot_qlearner.decide_next_action(True)

        try:
            self.initial_control_state = eval(str(next_action))
        except Exception as e:
            print next_action
            print e

        state = self.to_state([fp1, fp2, fp3])
        self.robot_foot_qlearner.update_state(state)


        return self.initial_control_state



def main():
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    # Panda Imports
    from panda3d.core import loadPrcFile


    # Load the PRC Configuration FIle
    loadPrcFile("orbital.prc")

    t = Simulation()
    t.run()






if __name__ == "__main__":
    main()
