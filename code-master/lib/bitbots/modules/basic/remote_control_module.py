#-*- coding:utf-8 -*-
"""
remoteControlModule
^^^^^^^^^^^^^^^^^^^

das module ließt Mithilfe des evdev framework die Befehle der Inputdevices aus und mappt sie auf Befehle etc.

Das AbstractRemoteControlModule macht das auslesen und mappen der Tastendrücke auf methoden wie vorwärts oder rechts,
die beiden implementierenden Klassen sorgen für die Richtige übertragung:

RobotRemoteControlModule, läuft als normales Modul auf dem Roboter und schreibt es daher die Befehle direkt ins Data,
PCRemoteControlModule nimmt einen udp socket (der kommt aus bin/remoteControl.py) und schreibt da die Daten für das
bitbots/modules/basic/network/network_remote_controller rein.

Wenn man eine weiteren Controller hinzufügen will kann man verbose auf true setzen und dann in der ausgabe vom
demo behaviour gucken, Wie der Controller heißt und ihn dann im getDevice hinzufügen.

Während dessen zeigt das Framework an wie die gedrückten Tasten gemappt werden, danach kann man filtern. Im
Zweifel bei den anderen Devices nachgucken ;)

Wenn das evdev Framework beim Tastendruck  abstürzt reicht u.U. die Keynummer in lib/evdev/evdev/ecodes in Zeile 76 mit
einem Mapping einzufügen

Wenn die devices nicht erkannt werden muss folgende Datei  (mit Sudo) erstellt werden:
/etc/udev/rules.d/50-remoteControl.rules

KERNEL=="mouse?", OWNER="darwin", MODE="600"
KERNEL=="mice", OWNER="darwin", MODE="600"
KERNEL=="event?", OWNER="darwin", MODE="600"

History:
''''''''

* 12.09.14 Created (0fiedler)
* 17.09.14 Ordentlicher gemacht (0fiedler)
"""

# Bevor ihr das auskommentiert probiert ein pip install evdev auf dem roboter
from evdev import InputDevice, categorize, ecodes, list_devices, RelEvent, KeyEvent, SynEvent, AbsEvent
from evdev.ecodes import REL, ABS

import socket
from bitbots.modules.abstract import AbstractThreadModule
import gevent.socket
import time
from bitbots.modules.keys import DATA_KEY_IPC, DATA_KEY_WALKING, DATA_KEY_WALKING_ACTIVE, DATA_KEY_WALKING_FORWARD, \
    DATA_KEY_WALKING_ANGULAR, DATA_KEY_WALKING_SIDEWARD, DATA_KEY_WALKING_ARMS, DATA_KEY_WALKING_HIP_PITCH_IN, \
    DATA_KEY_WALKING_HIP_PITCH_OUT, DATA_KEY_WALKING_FORWARD_REAL, DATA_KEY_WALKING_ANGULAR_REAL
from bitbots.util.speaker import say


class AbstractRemoteControlModule(object):
    def __init__(self):
        self.verbose = True

    def getDevice(self):
        if self.verbose:
            devices = map(InputDevice, list_devices())
            for dev in devices:
                print dev

        while True:
            self.device = None
            devices = map(InputDevice, list_devices())
            tmp = None
            for dev in devices:
                if 'Mouse' in dev.name:
                    self.type= 'Mouse'
                    self.device= dev.fn
                    tmp = dev
                if 'Dance Pad' in dev.name:
                    self.type = 'Dance Pad'
                    self.device = dev.fn
                    tmp = dev
                if 'Game Pad' in dev.name:
                    self.type = 'Game Pad'
                    self.device = dev.fn
                    tmp = dev
                if "360 pad" in dev.name:
                    self.type = "pad360"
                    self.device = dev.fn
                    tmp = dev
                if "Unifying" in dev.name:
                    self.type = "Unifying"
                    self.device = dev.fn
                    tmp = dev
            if self.device is not None:
                break
            time.sleep(1)
        if self.verbose:
            print tmp

    def listen(self):
        dev = InputDevice(self.device)
        try:
            for inputevent in dev.read_loop():
                try:
                    typedevent = categorize(inputevent)
                    if self.verbose:
                        self.infomode(inputevent, typedevent)
                    if self.type == 'Mouse':
                        self.mouse(inputevent,typedevent)
                    elif self.type == 'Dance Pad':
                        self.dancePad(inputevent,typedevent)
                    elif self.type == 'Game Pad':
                        self.gamepad(inputevent,typedevent)
                    elif self.type == "pad360":
                        self.pad360(inputevent,typedevent)
                    elif self.type == "Unifying":
                        self.keyboard(inputevent,typedevent)
                except KeyError as e:
                    if self.type == 'Game Pad': #Workaround for Game Pad
                        pass
        except IOError as e:
            if e.errno == 19:
                self.say('Lost Controller')
                self.getDevice()
                self.listen()
            else:
                raise

    def keyboard(self,inputevent,typedevent):
        if isinstance(typedevent, KeyEvent):
            kc = typedevent.keycode
            if kc is 'KEY_W' and inputevent.value == 0:
                self.forward()
            if kc is 'KEY_A' and inputevent.value == 0:
                self.left()
            if kc is 'KEY_D' and inputevent.value == 0:
                self.right()
            if kc is 'KEY_S' and inputevent.value == 0:
                self.backward()
            if kc is 'KEY_SPACE' and inputevent.value == 0:
                self.standStill()
            if kc is 'KEY_Q' and inputevent.value == 0:
                self.play('lk')
            if kc is 'KEY_E' and inputevent.value == 0:
                self.play('rk')
            if kc is 'KEY_UP' and inputevent.value == 0:
                self.lookup()
            if kc is 'KEY_DOWN' and inputevent.value == 0:
                self.lookdown()
            if kc is 'KEY_LEFT' and inputevent.value == 0:
                self.lookleft()
            if kc is 'KEY_RIGHT' and inputevent.value == 0:
                self.lookright()


    def gamepad(self,inputevent,typedevent):
        if isinstance(typedevent, AbsEvent):
            kc = ABS[typedevent.event.code]
            if kc is 'ABS_Y':
                if inputevent.value == 0:
                    self.forward()
                if inputevent.value == 127:
                    self.backward()
            if kc is 'ABS_X':
                if inputevent.value == 0:
                    self.backward()
                if inputevent.value == 127:
                    self.backward()
        if isinstance(typedevent, KeyEvent):
            kc = typedevent.keycode
            if kc is 'BTN_TR' and inputevent.value == 0:
                self.play('rk')
            if kc is 'BTN_TL' and inputevent.value == 0:
                self.play('lk')
            if 'BTN_A' in kc and inputevent.value == 1:
                self.standStill()
            if 'BTN_B' in kc and inputevent.value == 0:
                self.play('hi')
            if 'BTN_C' is kc and inputevent.value == 0:
                self.say('out of my way')
            if 'BTN_X' in kc and inputevent.value == 0:
                self.say('Moin')
            if 'BTN_Y' in kc and inputevent.value == 0:
                self.play('liegestuetze')
            if 'BTN_Z' is kc and inputevent.value == 0:
                self.say('Howdy, how are you')

    def mouse(self,inputevent,typedevent):
        if isinstance(typedevent, RelEvent):
            kc = REL[typedevent.event.code]
            if kc is 'REL_WHEEL':
                if inputevent.value == 1:
                    self.forward()
                else:
                    self.backward()
                print inputevent.value
        if isinstance(typedevent, KeyEvent):
            kc = typedevent.keycode
            if kc == 'BTN_MIDDLE' and inputevent.value == 1:
                self.standStill()
            if 'BTN_LEFT' in kc and inputevent.value == 0:
                self.backward()
            if 'BTN_RIGHT' == kc and inputevent.value == 0:
                self.backward()
            if 'BTN_SIDE' == kc and inputevent.value == 0:
                self.play('lk')
            if 'BTN_EXTRA' == kc and inputevent.value == 0:
                self.play('rk')
            print "KeyEvent", typedevent.keycode

    def dancePad(self,inputevent,typedevent):
        if isinstance(typedevent, AbsEvent):
            kc = ABS[typedevent.event.code]
            if kc is 'ABS_Y':
                if inputevent.value == 0:
                    self.forward()
                if inputevent.value == 255:
                    self.backward()
            if kc is 'ABS_X':
                if inputevent.value == 0:
                    self.left()
                if inputevent.value == 255:
                    self.right()
        if isinstance(typedevent, KeyEvent):
            kc = typedevent.keycode
            print inputevent.value
            if 'DancePad_UP' == kc and inputevent.value == 0:
                self.forward()
            if 'DancePad_DOWN' == kc and inputevent.value == 0:
                self.backward()
            if 'BTN_DEAD' == kc and inputevent.value == 0:
                self.backward()
            if 'DancePad_RIGHT' == kc and inputevent.value == 0:
                self.backward()
            if 'BTN_THUMB2' == kc and inputevent.value == 0:
                self.play('lk')
            if 'BTN_THUMB' == kc and inputevent.value == 0:
                self.play('rk')
            if 'BTN_BASE4' == kc and inputevent.value == 0:
               self.standStill()
            if 'BTN_TOP' == kc and inputevent.value == 0:
               self.say('Moin Moin')
            if 'BTN_TRIGGER' in kc and inputevent.value == 0:
                self.play('strike')
            if 'BTN_BASE3' == kc and inputevent.value == 0:
               self.say('Welcome to the Grand Elysee')
            #if 'BTN_TRIGGER' in kc:
            #    self.play('lk')

    def pad360(self,inputevent,typedevent):
        if isinstance(typedevent, AbsEvent):
            kc = ABS[typedevent.event.code]
            if kc is 'ABS_Z' and inputevent.value == 255:
                self.play('lk')
            if kc is 'ABS_RZ' and inputevent.value == 255:
                self.play('rk')
            if kc is 'ABS_Y':
                self.forwardabs((-5.0*inputevent.value)/32767)
            if kc is 'ABS_X':
                self.rightabs((-5.0*inputevent.value)/32767)
            if kc is 'ABS_RX':
                self.turnleftabs((-5.0*inputevent.value)/32767)
            if 'ABS_HAT0X' is kc:
                if inputevent.value == -1:
                    self.lookup()
                elif inputevent.value == 1:
                    self.lookdown()
            if 'ABS_HAT0Y' is kc:
                if inputevent.value == -1:
                    self.lookleft()
                elif inputevent.value ==1:
                    self.lookright()

        if isinstance(typedevent, KeyEvent):
            kc = typedevent.keycode
            if 'BTN_A' in kc and inputevent.value == 1:
                self.play('strike')
            if 'BTN_B' in kc and inputevent.value == 0:
                self.play('gruss2')
            if 'BTN_Y' in kc and inputevent.value == 0:
                self.say('out of my way')
            if 'BTN_X' in kc and inputevent.value == 0:
                self.say('Moin Moin')

    def infomode(self,inputevent,typedevent):
        if isinstance(typedevent, RelEvent):
            print "relEvent",inputevent.value
        if isinstance(typedevent, KeyEvent):
            print "KeyEvent", typedevent.keycode, '  Value ', inputevent.value
        if isinstance(typedevent, SynEvent):
            print 'synEvent', typedevent
        if isinstance(typedevent, AbsEvent):
            print 'absEvend', typedevent, '  keyCode ', ABS[typedevent.event.code], '  Value ', inputevent.value

    def standStill(self):
        raise NotImplementedError

    def forward(self):
        raise NotImplementedError

    def backward(self):
        raise NotImplementedError

    def right(self):
        raise NotImplementedError

    def left(self):
        raise NotImplementedError

    def turnright(self):
        raise NotImplementedError

    def turnleft(self):
        raise NotImplementedError

    def forwardabs(self, absValue):
        raise NotImplementedError

    def rightabs(self, absValue):
        raise NotImplementedError

    def turnleftabs(self, absValue):
        raise NotImplementedError

    def say(self, word):
        raise NotImplementedError

    def play(self, anim):
        raise NotImplementedError

    def lookdown(self):
        raise NotImplementedError

    def lookup(self):
        raise NotImplementedError

    def lookright(self):
        raise NotImplementedError

    def lookleft(self):
        raise NotImplementedError

class PCRemoteControlModule(AbstractRemoteControlModule):
    def __init__(self, socket):
        AbstractRemoteControlModule.__init__(self)
        self.socket = socket

    def start(self):
        self.getDevice()
        self.listen()

    def send(self, data):
        print "Send: %s" % data
        self.socket.send(data)

    def standStill(self):
        self.send(" ")

    def forwardabs(self, absValue):
        self.send(absValue) #TODO !!

    def rightabs(self, absValue):
        self.send(absValue) # TODO !!

    def turnleftabs(self, absValue):
        self.send(absValue) # TODO !!

    def forward(self):
        self.send('w')

    def backward(self):
        self.send('s')

    def right(self):
        self.send('d')

    def left(self):
        self.send('a')

    def turnleft(self):
        raise NotImplementedError

    def turnright(self):
        raise NotImplementedError

    def say(self, text):
        self.send('say '+ text)

    def play(self, anim):
        self.send('play ' + anim)

    def lookleft(self):
        self.send('j')

    def lookdown(self):
        self.send('k')

    def lookup(self):
        self.send('8')

    def lookright(self):
        self.send('u')

class RobotRemoteControlModule(AbstractThreadModule, AbstractRemoteControlModule):
    def __init__(self):
        AbstractThreadModule.__init__(
            self,
            requires=[],
            provides=[]
        )
        AbstractRemoteControlModule.__init__(self)

    def start(self, data):
        self.data = data
        AbstractThreadModule.start(self,data)

    def run(self):
        self.getDevice()
        self.listen()

    def standStill(self):
        print "still"
        self.data[DATA_KEY_WALKING_ACTIVE] = False
        self.data[DATA_KEY_WALKING_FORWARD] = 0
        self.data[DATA_KEY_WALKING_ANGULAR] = 0
        self.data[DATA_KEY_WALKING_SIDEWARD] = 0

    def forward(self):
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_FORWARD] += 1
        self.isWalkingActive()

    def backward(self):
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_FORWARD] -= 1
        self.isWalkingActive()

    def right(self):
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_SIDEWARD] -= 1
        self.isWalkingActive()

    def left(self):
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_SIDEWARD] += 1
        self.isWalkingActive()

    def turnleft(self):
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_ANGULAR] += 1
        self.isWalkingActive()

    def turnright(self):
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_ANGULAR] -= 1
        self.isWalkingActive()

    def forwardabs(self, absValue):
        print "forwad", round(absValue)
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_FORWARD] = round(absValue)
        self.isWalkingActive()

    def rightabs(self, absValue):
        print "right" , round(absValue)
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_SIDEWARD] = round(absValue)
        self.isWalkingActive()

    def turnleftabs(self, absValue):
        self.data[DATA_KEY_WALKING_ACTIVE] = True
        self.data[DATA_KEY_WALKING_ANGULAR] = round(absValue)
        self.isWalkingActive()

    def isWalkingActive(self):
        if self.data[DATA_KEY_WALKING_ANGULAR] == 0 and self.data[DATA_KEY_WALKING_FORWARD] == 0 and self.data[DATA_KEY_WALKING_SIDEWARD] == 0:
            self.data[DATA_KEY_WALKING_ACTIVE] = False
        else:
            self.data[DATA_KEY_WALKING_ACTIVE] = True

    def say(self, text):
        print "say", text
        say(text)

    def play(self, anim):
        print "play", anim
        self.data[DATA_KEY_WALKING_ACTIVE] = False
        self.data[DATA_KEY_WALKING_FORWARD] = 0
        self.data[DATA_KEY_WALKING_ANGULAR] = 0
        self.data[DATA_KEY_WALKING_SIDEWARD] = 0
        self.data["Animation"] = anim

    def lookdown(self):
        pose = self.data[DATA_KEY_IPC].get_pose()
        try:
            pose.head_pan.goal = pose.head_pan.position + 10
            self.data[DATA_KEY_IPC].update(pose)
        except ValueError:
            print "Invalid Value for Head Position\n\r"

    def lookup(self):
        pose = self.data[DATA_KEY_IPC].get_pose()
        try:
            pose.head_pan.goal = pose.head_pan.position - 10
            self.data[DATA_KEY_IPC].update(pose)
        except ValueError:
            print "Invalid Value for Head Position\n\r"



    def lookright(self):
        pose = self.data[DATA_KEY_IPC].get_pose()
        try:
            pose.head_tilt.goal = pose.head_tilt.position + 10
            self.data[DATA_KEY_IPC].update(pose)
        except ValueError:
            print "Invalid Value for Head Position\n\r"

    def lookleft(self):
        pose = self.data[DATA_KEY_IPC].get_pose()
        try:
            pose.head_tilt.goal = pose.head_tilt.position - 10
            self.data[DATA_KEY_IPC].update(pose)
        except:
            print "Invalid Value for Head Position\n\r"

def register(ms):
    ms.add(RobotRemoteControlModule, 'RemoteControlModule', requires=[], provides=[])
