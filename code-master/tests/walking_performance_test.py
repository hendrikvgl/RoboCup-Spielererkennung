#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
@author Robert

Ein Test zum beurteilen der Performance der Walkingengine.
Startet das Walking, macht tausende Iterationen und gibt die Resultate
auf der Konsole aus.
"""
import time
from bitbots.motion.zmpwalking import ZMPWalkingEngine

zm=ZMPWalkingEngine()

zm.start()
zm.velocity=(0.5,0,0)
cycles = 100000

print "Starte Messung mit ", str(cycles) ," Zyklen"
startime = time.time()
for i in range(cycles):
    zm.process()
endtime = time.time()
intervall = endtime - startime

print "Für ",str(cycles)," Updatezyklen wurden ",str(intervall)," Sekunden benötig. ",str(cycles/intervall)," fps"
