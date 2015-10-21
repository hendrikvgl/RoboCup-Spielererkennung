#-*- coding:utf-8 -*-
"""
DynamicThrowModule
^^^^^^^^^^^^^^^^^
Entwickelt im Robo-Cup Praktikum SoSe 2014

Dieses Modul dient der Demonstration des angepassten Einwurfs.
Falls es mit dem Demoverhalten gestartet wird:
Motion muss mit --nostandup gestartet werden, sonst funktioniert es nicht!
Der Roboter wartet darauf, dass der Ball in einen Bereich kommt, in dem er ihn greifen kann. Dann bückt
er sich, positioniert seine Arme auf der Höhe ds Balls und greift zu. Wenn er den Ball gegriffen hat,
macht er danach einen Einwurf, wenn nicht geht er wieder in Ausgangsposition.

An folgenden Stellen kann das Verhalten angepasst/verbessert werden:
- Bereich, in dem er den Ball als greifbar identifiziert
- Umrechnung der Ballentfernung in Parameter
- Beim Werfen (wurf_neu.json) kommt er mit dem Ball manchmal gegen seinen Kopf
- Wann der Wurf abgebrochen wird (1100 gab bis jetzt noch keine Fehlentscheidungen)

Verwendete Animationen:
"einwurf_init2"
"einwurf_ende2"
"wurf_neu"

History:
''''''''

* 26.8.14: Created (Anne-Victoria Meyer, Benjamin Scholz, Tim Dobert)


"""

from bitbots.modules.abstract.abstract_module import AbstractModule
from bitbots.modules.keys import DATA_KEY_BALL_FOUND, DATA_KEY_BALL_INFO, \
                                DATA_KEY_IPC
from bitbots.util.speaker import say, get_config

from bitbots.util.animation import play_animation
from bitbots.robot.pypose import *
from bitbots.ipc.ipc import *
import numpy as np
import time

class DynamicThrowModule(AbstractModule):
    
    def __init__(self):
        #Mitten im Bewegungsablauf muss ein Update erfolgen
        self.throwing = False
        
    def start(self, data):
        self.ipc = data[DATA_KEY_IPC]
        self.pose = self.ipc.get_pose()
        
        #Bereit machen
        play_animation("walkready_haende", self.ipc)
        self.pose.head_tilt.speed = 90
        self.pose.head_pan.speed = 90
        self.pose.head_tilt.goal = -74
        self.pose.head_pan.goal = 0
        self.ipc.update(self.pose)
        self.wait_for_end()
        
    def update(self, data):
        if not self.throwing :
            if data[DATA_KEY_BALL_FOUND]:
                ball_info = data[DATA_KEY_BALL_INFO]
                if ball_info.u >= 60 and ball_info.u <= 130  and abs(ball_info.v) <= 20 :  #Ball in Reichweite
                    param = (ball_info.u - 60) * (100/70)  #Umrechnung
                    self.throwing = True
                    self.pick_up(param)
        else: #Wurf beenden
            if data.get("42", "") > 1100:   # Wenn er den Ball in er Hand hat
                self.play("wurf_stark", self.ipc)
            self.throwing = False
            self.play("walkready_haende", self.ipc)
            self.wait_for_end()
            self.pose = self.ipc.get_pose()
            self.pose.head_tilt.speed = 90
            self.pose.head_tilt.goal = -74
            self.ipc.update(self.pose)
            self.wait_for_end()
            
    
    def wait_for_end(self):
        """
        Wartefunktion um Animationen vollständig abzuspielen
        """
        time.sleep(0.05)
        while (not self.ipc.controlable) or self.ipc.get_state() == STATE_ANIMATION_RUNNING:
            time.sleep(0.01)

    def play(self, animation, ipc):
        """
        Spielt eine Animation dann ab, wenn gerade keine anderen Bewegungen stattfinden
        """
        self.wait_for_end()
        play_animation(animation, ipc)
    
    #Hebt den Ball auf. Parameter kann 0 bis 100 sein
    def pick_up(self, param):
        """
        Der Roboter bückt sich um den Ball aufzuheben.
        
        :param param: Wert von 0 bis 100, wie weit vorne der Roboter greifen soll.
        :type param: int
        """
        if param > 100:
            param = 100
        if param < 0:
            param = 0
        d = 90 + 0.3 * param
        
        self.play("einwurf_init2", self.ipc)
        #Geschwindigkeiten-------------------
        self.pose.head_pan.speed = 90
        self.pose.head_tilt.speed = 90
        self.pose.l_ankle_pitch.speed = 90
        self.pose.l_ankle_roll.speed = 90
        self.pose.l_elbow.speed = 90
        self.pose.l_hip_pitch.speed = 90
        self.pose.l_hip_roll.speed = 90
        self.pose.l_hip_yaw.speed = 90
        self.pose.l_knee.speed = 90
        self.pose.l_shoulder_pitch.speed = 90
        self.pose.l_shoulder_roll.speed = 90
        self.pose.r_ankle_pitch.speed = 90
        self.pose.r_ankle_roll.speed = 90
        self.pose.r_elbow.speed = 90
        self.pose.r_hip_pitch.speed = 90
        self.pose.r_hip_roll.speed = 90
        self.pose.r_hip_yaw.speed = 90
        self.pose.r_knee.speed = 90
        self.pose.r_shoulder_pitch.speed = 90
        self.pose.r_shoulder_roll.speed = 90
        #1. Position: Ausrichten------------------
        self.wait_for_end()
        self.pose.head_pan.goal = 0.0
        self.pose.head_tilt.goal = 0.0
        self.pose.l_ankle_pitch.goal = 20.0 #anders als im nächsten, wichtig?
        self.pose.l_ankle_roll.goal = 0.0
        self.pose.l_elbow.goal = 80.0
        self.pose.l_hip_pitch.goal = 98.0
        self.pose.l_hip_roll.goal = 0
        self.pose.l_hip_yaw.goal = 0
        self.pose.l_knee.goal = 0
        # Paramter hier v
        self.pose.l_shoulder_pitch.goal = -d
        self.pose.l_shoulder_roll.goal = 20.0
        self.pose.r_ankle_pitch.goal = -20.0 #anders als im nächsten, wichtig?
        self.pose.r_ankle_roll.goal = 0.0
        self.pose.r_elbow.goal = -80.0
        self.pose.r_hip_pitch.goal = -98.0
        self.pose.r_hip_roll.goal = 0
        self.pose.r_hip_yaw.goal = 0
        self.pose.r_knee.goal = 0
        # Paramter hier v
        self.pose.r_shoulder_pitch.goal = d
        self.pose.r_shoulder_roll.goal = -20.0
        self.ipc.update(self.pose)
        time.sleep(0.75)
        #2. Position: Zugreifen--------------------
        self.pose.head_pan.goal = 0.0
        self.pose.head_tilt.goal = 0.0
        self.pose.l_ankle_pitch.goal = 17.0
        self.pose.l_ankle_roll.goal = 0
        self.pose.l_elbow.goal = 80.0
        self.pose.l_hip_pitch.goal = 98.0
        self.pose.l_hip_roll.goal = 0
        self.pose.l_hip_yaw.goal = 0
        self.pose.l_knee.goal = 0
        # Paramter hier v
        self.pose.l_shoulder_pitch.goal = -d
        self.pose.l_shoulder_roll.goal = 40.0
        self.pose.r_ankle_pitch.goal = -17.0
        self.pose.r_ankle_roll.goal = 0
        self.pose.r_elbow.goal = -80.0
        self.pose.r_hip_pitch.goal = -98.0
        self.pose.r_hip_roll.goal = 0
        self.pose.r_hip_yaw.goal = 0
        self.pose.r_knee.goal = 0
        # Paramter hier v
        self.pose.r_shoulder_pitch.goal = d
        self.pose.r_shoulder_roll.goal = -40.0
        self.ipc.update(self.pose)
        time.sleep(0.75)
        #Endanimation---------------------------
        self.play("einwurf_ende2", self.ipc)
        self.wait_for_end()
        
    
def register(ms):
    ms.add(DynamicThrowModule, "DynamicThrowModule",
           requires=[DATA_KEY_BALL_INFO, DATA_KEY_BALL_FOUND, DATA_KEY_IPC],
           provides=[])
