#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bitbots.ipc.ipc import SharedMemoryIPC
from bitbots.util.speaker import say
from bitbots.util import get_config
from bitbots.util.resource_manager import ResourceManager
from bitbots.debug import Scope
from bitbots.util.animation import play_animation
import socket

CAMERA_INDEX = 0
ipc = SharedMemoryIPC()
config = get_config()
debug = Scope("demo")
rm = ResourceManager()
class Demo(object):
    def __init__(self):
        self.anim_playing = False


    def anim_calback(self, flag):
        self.anim_playing = False

    def play_anim(self, anim, block=False):
        self.anim_playing = True
        play_animation(anim, ipc, self.anim_calback)
        if block:
            while self.anim_playing:
                pass

    def start(self):
        hostname = socket.gethostname()

        say("Hello my name is " + hostname, False)
        self.play_anim("hi", True)
        say("I'm a Darwin robot. I play for the Hamburg Bit Bots. We are a group of students of the university of hamburg that participates in the robocup.", False)
        self.play_anim("talk1", True)
        say("Now I will show you what I can do.", False)
        self.play_anim("KopfStand", True)
        self.play_anim("freddy", True)
        self.play_anim("talk1", False)
        say("I know this was really impressiv, but I can do many other things too", True)
        say("for example I can do a kick", True)
        self.play_anim("rk", True)
        say("and with the other leg too of course", True)
        self.play_anim("lk", True)
        self.play_anim("talk1", False)
        say("I think I'm a bit out of shape. I better do some push ups", True)
        self.play_anim("liegestuez", True)
        self.play_anim("init", True)
        self.play_anim("brucelee", True)
        say("now I will do a litle dance")
        self.play_anim("jogram", True)
        say("It was nice to meet you. I hope you liked my show. I'm finished. I'm going to sleep now", True)
        self.play_anim("hinsetzen")


demo = Demo()
demo.start()
