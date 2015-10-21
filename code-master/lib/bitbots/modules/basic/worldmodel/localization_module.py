#-*- coding:utf-8 -*-
"""
LocalizationModule
^^^^^^^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>


Absolute Coordinate System
--------------------------

The origin of the absolute coordinate center is the center of the middle
circle (center of field). The x axis points towards the opponent goal, the
y axis to the left.::

          y
          ^       ______________________
          |     M |          |          |  O
          |     Y |_  -x, y  |  x, y   _|  P
          |     G | |        |        | |  P
     0    +     O | |       ( )       | |  G
          |     A |_|        |        |_|  O
          |     L |   -x,-y  |  x,-y    |  A
          |       |__________|__________|  L
          |
          +------------------+--------------> x
                             0

The orientation of the robot is measured in degrees and is zero along the positive X-axis.
So the goalie standing on the goal line has the triple (-4500, 0, 0) for its global position

History:
* 8/17/14: Created (sheepy)

This is a convenience module which is using whatever source to inject the global position and orientation into the
data dictionary. Currently it is listening on a UDP Socket to get the position.

"""
import socket
import time
from bitbots.modules.abstract import AbstractThreadModule
from bitbots.modules.keys import DATA_KEY_POSITION
from bitbots.util import get_config

config = get_config()

class KeepAliveRobotPackage():

    @staticmethod
    def build_package():
        return "KAL"


class PositionSettingPackage():

    @staticmethod
    def build_package(player, x, y, orientation, direction):
        """
        :param player: The player as target or source
        :param x: The setting or setted x-value
        :param y: The setting or setted y-value
        :param orientation: The setting or setted orientation
        :param direction:The direction - 1 is towards the robot 0 for ack to system
        """
        return "POS" + ";".join([str(player), str(x), str(y), str(orientation), str(direction)])

    @staticmethod
    def from_string(payload):
        player, x, y, orientation, direction = payload.split(";")
        return int(player), int(x), int(y), int(orientation), int(direction)


class LocalizationModule(AbstractThreadModule):

    def __init__(self):
        super(LocalizationModule, self).__init__(
            requires=[],
            provides=[DATA_KEY_POSITION]
        )

        self.player = config["PLAYER"]
        print "Player id", self.player
        self.port = 9050+int(self.player)

    def start(self, data):
        super(LocalizationModule, self).start(data)
        self.set(DATA_KEY_POSITION, None)
        print "START UP LOCALIZATION INJECT MODULE"

    def run(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("0.0.0.0", self.port))
            print "Bound UDP-Socket to port", self.port

            while True:
                data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
                print "Got package from", data, addr

                package_length = self.determine_package_length(data[0:2])
                package = data[2:package_length+2]

                command, info = package[0:3], package[3:package_length]

                if command == "POS":
                    psp = PositionSettingPackage.from_string(info)
                    player, x, y, orientation, direction = psp
                    if direction == 1:
                        # Send the ack package
                        if player == self.player:
                            # WE GOT CENTIMETERS BY THE GUI SO TIMES 10
                            print "Injected Position", 10*x, 10*y, orientation
                            self.set(DATA_KEY_POSITION, [10*x, 10*y, orientation])
                            msg = PositionSettingPackage.build_package(player, x, y, orientation, 0)
                            self.send_message(sock, msg,addr)

                if command == "KAL":
                    #Keep Alive Package so just resend one
                    msg = KeepAliveRobotPackage.build_package()
                    self.send_message(sock, msg, addr)

                time.sleep(0.5)
        except:
            print "Error in Localization Injector Model"


    def determine_package_length(self, chrs):
        assert len(chrs) == 2
        return ord(chrs[0]) * 16 + ord(chrs[1])

    def calc_prefix_chars(self, length):
        a = length / 16
        b = length % 16
        prefix = chr(a) + chr(b)
        return prefix

    def send_message(self, sock, message, udp_info):
        total_len = len(message)
        assert total_len <= 255

        prefix = self.calc_prefix_chars(total_len)

        sock.sendto(prefix+message, udp_info)

def register(ms):
    ms.add(LocalizationModule, "LocalizationModule",
           requires=[],
           provides=[DATA_KEY_POSITION])
