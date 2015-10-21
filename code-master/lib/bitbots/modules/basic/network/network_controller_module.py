#-*- coding:utf-8 -*-
"""
NetworkControllerModule
^^^^^^^^^^^^^^^^^^^^^^^

Listens to instructions on the network, e.g. for letting our robot walk via network with the wlkscript.

History:
''''''''

* ??.??.??: Created (Nils Rokita)

* 06.08.14 Refactor (Marc Bestmann)

"""
import socket

from bitbots.modules.abstract import AbstractModule
from bitbots.util.speaker import say
from bitbots.modules.keys import DATA_KEY_IPC, DATA_KEY_WALKING, DATA_KEY_WALKING_ACTIVE, DATA_KEY_WALKING_FORWARD, \
    DATA_KEY_WALKING_ANGULAR, DATA_KEY_WALKING_SIDEWARD, DATA_KEY_WALKING_ARMS, DATA_KEY_WALKING_HIP_PITCH_IN, \
    DATA_KEY_WALKING_HIP_PITCH_OUT, DATA_KEY_WALKING_FORWARD_REAL, DATA_KEY_WALKING_ANGULAR_REAL, \
    DATA_KEY_WALKING_SIDEWARD_REAL


class NetworkControllerModule(AbstractModule):
    def __init__(self):

        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setblocking(0)  # nonblocking
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', 12345))

    def update(self, data):
        try:
            packet, addr = self.socket.recvfrom(50)
        except:  # timeout and stuff
            return
        out = ""
        if packet[-1] == '\n':
            packet = packet[0:-1]
        if packet == 'w':
            data[DATA_KEY_WALKING_ACTIVE] = True
            data[DATA_KEY_WALKING_FORWARD] += 1
        elif packet == 's':
            data[DATA_KEY_WALKING_ACTIVE] = True
            data[DATA_KEY_WALKING_FORWARD] -= 1
        elif packet == 'a':
            data[DATA_KEY_WALKING_ACTIVE] = True
            data[DATA_KEY_WALKING_ANGULAR] += 1
        elif packet == 'd':
            data[DATA_KEY_WALKING_ACTIVE] = True
            data[DATA_KEY_WALKING_ANGULAR] -= 1
        elif packet == 'g':
            data[DATA_KEY_WALKING_ACTIVE] = True
            data[DATA_KEY_WALKING_SIDEWARD] -= 1
        elif packet == 'f':
            data[DATA_KEY_WALKING_ACTIVE] = True
            data[DATA_KEY_WALKING_SIDEWARD] += 1
        elif packet == 'q':
            data[DATA_KEY_WALKING_ACTIVE] = True
        elif packet == 'o':
            data[DATA_KEY_WALKING_ARMS] = not data[DATA_KEY_WALKING_ARMS]
        elif packet == 'i':
            pose = data[DATA_KEY_IPC].get_pose()
            try:
                pose.head_pan.goal = pose.head_pan.position - 10
                data[DATA_KEY_IPC].update(pose)
            except ValueError:
                out += "Invalid Value for Head Position\n\r"
        elif packet == 'u':
            pose = data[DATA_KEY_IPC].get_pose()
            try:
                pose.head_pan.goal = pose.head_pan.position + 10
                data[DATA_KEY_IPC].update(pose)
            except ValueError:
                out += "Invalid Value for Head Position\n\r"
        elif packet == 'j':
            pose = data[DATA_KEY_IPC].get_pose()
            try:
                pose.head_tilt.goal = pose.head_tilt.position + 10
                data[DATA_KEY_IPC].update(pose)
            except ValueError:
                out += "Invalid Value for Head Position\n\r"
        elif packet == '8':
            pose = data[DATA_KEY_IPC].get_pose()
            try:
                pose.head_tilt.goal = pose.head_tilt.position - 10
                data[DATA_KEY_IPC].update(pose)
            except:
                out += "Invalid Value for Head Position\n\r"
        elif packet == '.':
            data[DATA_KEY_WALKING_HIP_PITCH_IN] = data[DATA_KEY_WALKING_HIP_PITCH_OUT] + 1
            out += "Hip Pitch is now " + str(
                data[DATA_KEY_WALKING_HIP_PITCH_IN]) + "\n\r"
        elif packet == ',':
            data[DATA_KEY_WALKING_HIP_PITCH_IN] = data[DATA_KEY_WALKING_HIP_PITCH_OUT] - 1
            out += "Hip Pitch is now " + str(
                data[DATA_KEY_WALKING_HIP_PITCH_IN]) + "\n\r"
        elif packet == ' ':
            out += "Walking Stopped\n\r"
            data[DATA_KEY_WALKING_ACTIVE] = False
            data[DATA_KEY_WALKING_FORWARD] = 0
            data[DATA_KEY_WALKING_ANGULAR] = 0
            data[DATA_KEY_WALKING_SIDEWARD] = 0
        elif len(packet) > 4 and packet[0:4] == 'play':
            data[DATA_KEY_WALKING_ACTIVE] = False
            data[DATA_KEY_WALKING_FORWARD] = 0
            data[DATA_KEY_WALKING_ANGULAR] = 0
            data[DATA_KEY_WALKING_SIDEWARD] = 0
            data["Animation"] = packet[5:]
            out += "Play Animation " + packet[5:] + "\n\r"
        elif len(packet) > 3 and packet[0:3] == 'say':
            say(packet[5:])
        if data[DATA_KEY_WALKING_ACTIVE] is True:
            out += "Walking: True\n\r\tForward: %d\n\r\tSideward: %d\n\r\tAngular: %d\n\r" % (
                data[DATA_KEY_WALKING_FORWARD_REAL],
                data[DATA_KEY_WALKING_SIDEWARD_REAL],
                data[DATA_KEY_WALKING_ANGULAR_REAL])
        if out != "":
            self.socket.sendto(out, addr)


def register(ms):
    """Sich selbst registrieren"""
    ms.add(NetworkControllerModule, "NetworkController",
           requires=[DATA_KEY_IPC,
                     DATA_KEY_WALKING,
                     DATA_KEY_WALKING_ACTIVE,
                     DATA_KEY_WALKING_FORWARD,
                     DATA_KEY_WALKING_ANGULAR,
                     DATA_KEY_WALKING_SIDEWARD,
                     DATA_KEY_WALKING_ARMS,
                     DATA_KEY_WALKING_HIP_PITCH_OUT,
                     DATA_KEY_WALKING_FORWARD_REAL],
           provides=[DATA_KEY_WALKING_HIP_PITCH_IN])
