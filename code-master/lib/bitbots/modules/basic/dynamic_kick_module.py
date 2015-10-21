#-*- coding:utf-8 -*-
"""
DynamicKickModule
^^^^^^^^^^^^^^^^^
Entwickelt im Robo-Cup Praktikum SoSe 2014

Dieses Modul dient zur Demonstration von mit inverser Kinematik angepassten Schüssen.
Falls es mit dem Demoverhalten gestartet wird: 
Der Roboter wartet, dass ein Ball in sein Sichtfeld kommt und entscheidet dann, ob er schießt 
und wenn ja, mit welchem Fuß und wie er ihn bewegt. je weiter außen der Ball liegt, desto mehr
bewegt er auch den Fuß nach außen.
Stabilität kann noch verbessert werden, besonders bei Schüssen weit außen.

An folgenden Stellen kann das Verhalten noch angepasst/verbessert werden:
- Start- und Endanimationen (z.B. "lk_start"
- Positionsdaten für díe inverse Kinematik
- Parametrisierung der Schussfunktion
- Bereich, in dem sichder Ball befinden muss, damit der Roboter schießt

Verwendete Animationen:
"lk_start"
"lk_end"
"rk_start"
"rk_end"
Links und rechts sind jeweils gespiegelt


History:
''''''''

* 22.8.14: Created (Anne-Victoria Meyer, Benjamin Scholz, Tim Dobert)


"""

from bitbots.modules.abstract.abstract_module import AbstractModule
from bitbots.modules.keys import DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO, \
                                DATA_KEY_IPC
from bitbots.util.speaker import say, get_config

from bitbots.util.animation import play_animation
from bitbots.robot.kinematics import *
from bitbots.robot.pypose import *
from bitbots.ipc.ipc import *
import numpy as np
import time

class DynamicKickModule(AbstractModule): #todo this should be deleted as soon as the dynamic kick works in the behaviour
    
    def __init__(self):
        pass
        
    def start(self, data):
        #Für Kinematik:
        self.ipc = data[DATA_KEY_IPC]
        self.pose = self.ipc.get_pose()
        self.robot = Robot()
        self.task = KinematicTask(self.robot)
        self.robot.update(self.pose)
        
        play_animation("walkready", self.ipc)
        self.pose.head_tilt.speed = 90
        self.pose.head_pan.speed = 90
        self.pose.head_tilt.goal = -74
        self.pose.head_pan.goal = 0
        self.ipc.update(self.pose)
        self.wait_for_end()
        
    def update(self, data):
        if data[DATA_KEY_BALL_FOUND]:
            ball_info = data[DATA_KEY_BALL_INFO]
            if abs(ball_info.v) <= 150 and ball_info.u < 110 :  #Schussbereich
                self.kick(ball_info.v)
    
    def wait_for_end(self):
        """
        Wartefunktion um Animationen und Kinematik vollständig abzuspielen
        """
        time.sleep(0.05)
        while (not self.ipc.controlable) or self.ipc.get_state() == STATE_ANIMATION_RUNNING:
            time.sleep(0.01)
    
    #Schussfunktion. ballV sollte ball_info.v sein
    def kick(self, ballV):
        """
        Führt den Schuss aus
        :param ballV: Sollte data[DATA_KEY_BALL_INFO].v sein.
                      Steuert, wie weit Außen der Tritt erfolgt
        :type ballV: int
        """
        param = abs(ballV) - 50   #Position in Parameter umrechnen, geht vielleicht schlauer?
        root = 0
        #Entscheidung für die Seite
        if ballV > 0:  #links
            lr = 1
            end_joint = 35
            angle_task_joints = [16]
            ignore_joints = [8, 18]
            start = "lk_start"
            ende = "lk_end"
        else:   #rechts
            lr = -1
            end_joint = 34
            angle_task_joints = [15]
            ignore_joints = [7, 17]
            start = "rk_start"
            ende = "rk_end"
            
        if param > 100:
            param = 100
        if param < 0:
            param = 0
        
        #Berechnung der Kinematischen Positionen
        x = 140 - 0.4 * param
        y1 = lr * (40 + 0.5 * param)
        y2 = y1 + lr * (0.05 * param) #Für Stabilität vielleicht y2 = y1
        
        #Starten des Schussvorgangs
        play_animation(start, self.ipc)
        self.wait_for_end()
        self.robot.update(self.ipc.get_pose())
        #1. kinematische Position
        self.task.perform(root, end_joint, [(1, 0, 0), np.array((0, y1, -280))], (1e-2, 1), (0, 3), 100, angle_task_joints, ignore_joints)
        self.robot.set_angles_to_pose(self.pose)
        self.ipc.update(self.pose)
        self.wait_for_end()
        self.robot.update(self.ipc.get_pose())
        #2. kinematische Position
        self.task.perform(root, end_joint, [(1, 0, 0), np.array((x, y2, -240))], (1e-2, 1), (0, 3), 100, angle_task_joints, ignore_joints)
        self.robot.set_angles_to_pose(self.pose)
        #Bewegung der Arme und des anderen Beins für Gleichgewicht/Stabilität
        if lr==1 :
            self.pose.l_shoulder_pitch.goal = 61.69921875
            self.pose.l_elbow.goal = -0.703125
            self.pose.r_knee.goal = 55.283203125
            self.pose.r_ankle_roll.goal = -9.4921875
            self.pose.r_ankle_pitch.goal = 27.421875
            self.pose.r_hip_yaw.goal = -0.703125
            self.pose.r_hip_roll.goal = 2.8125
            self.pose.r_hip_pitch.goal = -40.517578125
            self.pose.r_shoulder_pitch.goal = -15.64453125
            self.pose.r_elbow.goal = 49.39453125 
        else:
            self.pose.r_shoulder_pitch.goal = -61.69921875
            self.pose.r_elbow.goal = 0.703125
            self.pose.l_knee.goal = -55.283203125
            self.pose.l_ankle_roll.goal = 9.4921875
            self.pose.l_ankle_pitch.goal = -27.421875
            self.pose.l_hip_yaw.goal = 0.703125
            self.pose.l_hip_roll.goal = -2.8125
            self.pose.l_hip_pitch.goal = 40.517578125
            self.pose.l_shoulder_pitch.goal = 15.64453125
            self.pose.l_elbow.goal = -49.39453125
        self.ipc.update(self.pose)
        self.wait_for_end()
        play_animation(ende, self.ipc)
        self.wait_for_end()
        play_animation("walkready", self.ipc)
        self.wait_for_end()
    
def register(ms):
    ms.add(DynamicKickModule, "DynamicKickModule",
           requires=[DATA_KEY_BALL_INFO, DATA_KEY_BALL_FOUND, DATA_KEY_IPC],
           provides=[])
