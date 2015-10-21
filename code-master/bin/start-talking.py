#!/usr/bin/env python
#-*- coding:utf-8 -*-

import random
import time
import os

#from bitbots.util import say

#from bitbots.debug import Scope

#debug = Scope("Talking")

def say_all_words():

    for i in range(100):
        d1 = int(random.random()*7)
        d2 = int(random.random()*10)
        d3 = int(random.random()*10)

        string = "Distance. %i. Point. %i. %i. Meter" % (d1, d2, d3)
        os.system("espeak \"%s.\""  % (string))
        time.sleep(1)

    os.system("espeak \"Distance.\"")
    time.sleep(1)
    os.system("espeak \"Point.\"")
    time.sleep(1)
    os.system("espeak \"Meter.\"")
    time.sleep(1)
    for i in range(10):
        os.system("espeak \"%i.\""  % (i))
        time.sleep(1)

while(True):
    say_all_words()

