#-*- coding:utf-8 -*-
"""
Simulationbridge
^^^^^^^^^^^^^^^^

.. moduleauthor:: Nils Rokita <0rokita@informatik.uni-hamburg.de>


History:

* 12.05.13: Created (Nils Rokita)

* 21.05.13: Added DXLObjects (Nils Rokita)

* 08.08.13: Added Immage transports to ipc

Dieses Modul verbindet unsere Software mit einem Simulator (Simspark)
"""
from gevent import socket
import struct
import time
import math
import gevent
import numpy as np
#import vrep
from bitbots.debug import Scope
from bitbots.ipc.ipc import SharedMemoryIPC

ipc = SharedMemoryIPC()

pi = 3.141592653589793238462643383279502884197169
MOTOR_EFFECTOR = {
1: "rae1",
2: "lae1",
3: "rae2",
4: "lae2",
5: "rae3",
6: "lae3",
7: "rle1",
8: "lle1",
9: "rle2",
10: "lle2",
11: "rle3",
12: "lle3",
13: "rle4",
14: "lle4",
15: "rle5",
16: "lle5",
17: "rle6",
18: "lle6",
19: "he1",
20: "he2"}
MOTOR_PRECEPTOR = {
"raj1": 1,
"laj1": 2,
"raj2": 3,
"laj2": 4,
"raj3": 5,
"laj3": 6,
"rlj1": 7,
"llj1": 8,
"rlj2": 9,
"llj2": 10,
"rlj3": 11,
"llj3": 12,
"rlj4": 13,
"llj4": 14,
"rlj5": 15,
"llj5": 16,
"rlj6": 17,
"llj6": 18,
"hj1": 19,
"hj2": 20}

from bitbots.lowlevel.serial import AbsSerial
from bitbots.util import Joints

joints = Joints().all()


class DxlObject(object):
    """
    Diese Classe repräsentiert ein object im Dxl Buss System, und wird in der
    regel beerbt werden.
    """
    def __init__(self, id):
        self.data = {}

    def write_rigisters(self, start, registers):
        """
        Schreibt die Register registers ab der startposition start.

        :param start: Startadresse ab der geschrieben werden soll
        :type start: int
        :param registers: Die Daten die geschrieben werden sollen (Die Elemente
            der liste sollten ints in im wertebereich 0-0xFF sein)
        :type registers: list
        """
        i = 0
        for register in registers:
            self.data[start + i] = register
            #if start + i < 19:
            #    print "Write Register %d mit wert %s" % (start + i, register)
            i += 1

    def get_id(self):
        """
        Gibt die ID des Objektes zurück
        """
        return self.data[3]

    def get_chr_registers(self, reg):
        """
        Gitbt ein String der register zurück

        :param reg: Liste der Register welche zurückgegeben werden sollen
        :param reg: list
        """
        start = reg[0]
        length = reg[1]
        data = ""
        #print start, length, reg
        for i in range(0, length):
            data += chr(self.data[start + i])
        if len(data) != length:
            print len(data), length
        return data


class CM730(DxlObject):
    """
    Repräsentert ein CM730 Board. Die Register sind vorbelegt mit der
    Standartbelegung
    """
    def __init__(self, id):
        super(CM730, self).__init__(id)
        # preinitialisieren der register (cm370 hat viele mit 0)
        for i in range(0, 81):
            self.data[i] = 0
        self.data[0] = 0     # model
        self.data[1] = 115   # model
        self.data[2] = 1     # firmware
        self.data[3] = id    # id
        self.data[5] = 2     # status return level
        self.data[38] = 0    # gyro z Low
        self.data[39] = 2    # gyro z high
        self.data[40] = 0    # gyro y Low
        self.data[41] = 2    # gyro y high
        self.data[42] = 0    # gyro x Low
        self.data[43] = 2    # gyro x high
        self.data[44] = 0    # acc x Low
        self.data[45] = 2    # acc x high
        self.data[46] = 0    # acc y Low
        self.data[47] = 2    # acc y high
        self.data[48] = 0    # acc z Low
        self.data[49] = 2    # acc z high
        self.data[50] = 124  # present voltage

    def __repr__(self):
        return "<CM730>"


class MX28(DxlObject):
    """
    Repräsentiert einen Motor. Die Register sind mit den Defaultwerten
    vorbelegt
    """
    def __init__(self, id):
        super(MX28, self).__init__(id)
        #defaultbelegung
        self.data[0] = 29    # model
        self.data[1] = 0     # model
        self.data[2] = 30    # firmware
        self.data[3] = id    # id
        self.data[4] = 1     #
        self.data[5] = 0     #
        self.data[6] = 0     #
        self.data[7] = 0     #
        self.data[8] = 255   #
        self.data[9] = 15    #
        self.data[11] = 80   #
        self.data[12] = 60   #
        self.data[13] = 160  #
        self.data[14] = 255  #
        self.data[15] = 3    #
        self.data[16] = 2    #
        self.data[17] = 36   #
        self.data[18] = 0    #
        # RAM
        self.data[24] = 0    #
        self.data[25] = 0    #
        self.data[26] = 32   #
        self.data[27] = 0    #
        self.data[28] = 0    #
        self.data[30] = 0xFF    # goal L
        self.data[31] = 7    # goal H
        self.data[32] = 0    #
        self.data[33] = 0    #
        self.data[34] = 255  #
        self.data[35] = 3    #
        self.data[36] = 0    #
        self.data[37] = 0    #
        self.data[38] = 0    #
        self.data[39] = 0    #
        self.data[40] = 0    #
        self.data[41] = 0    #
        self.data[42] = 124  # voltage
        self.data[43] = 40   # temperatur
        self.data[44] = 0    #
        self.data[45] = 0    #
        self.data[46] = 0    #
        self.data[47] = 0    #
        self.data[48] = 32   #
        self.data[49] = 0    #

        self.data[73] = 0    # goal Accelaration (ab ~V32)

    def __repr__(self):
        return "<MX28 cid=%d pos=%d° goal=%d°>" % (self.data[3], self.get_position_angel(), self.get_goal())

    def get_goal(self):
        """
        gitbt die Goalposition des Motors zurück (wertebereich: 0-4095)
        """
        return self.data[30] + (self.data[31] << 8)

    def set_goal(self, angel):
        """
        Setzt das goal eines Motors, fürs debugen
        """
        self.data[30] = angel & 0xff
        self.data[31] = (angel >> 8) & 0xFF

    def set_position(self, angel):
        """
        Setzt die Istposition des Motors

        :param angel: Der Winkel der gesetzt werden soll
        """
        angel += 180.0
        angel = int((angel / 360) * 4095)
        self.data[36] = angel & 0xFF
        self.data[37] = (angel >> 8) & 0xFF

    def set_position_rad(self, rad):
        """
        Setzt die Istposition des Motors in radians
        :param rad:  der Winkel in radian
        """
        rad += pi
        wert = int((rad / (2*pi)) * 4095 )
        self.data[36] = wert & 0xFF
        self.data[37] = (wert >> 8) & 0xFF

    def get_position(self):
        """
        Gibt die aktuelle Position des Motors zurück
        """
        return (self.data[36] + (self.data[37] << 8))

    def get_position_angel(self):
        """
        Gibt die aktuelle Position des Motors in Grad zurück
        """
        return (((self.data[36] + (self.data[37] << 8)) / 4095.0) * 360) - 180

    def get_vrep_goal(self):
        value = (((self.data[30] + (self.data[31] << 8))/4095.0)*2*pi - pi)
        return value

    def get_simspark_value(self):
        """
        Gibt den Bewegungswert zurück der für Simspark gebraucht wird
        TODO: Geschwindigkeit besser berechnen!
        """
        #print self, self.get_goal()
        return (self.get_goal() - self.get_position()) / 314.0


class Simulatorbridge(AbsSerial):
    """

    """
    def __init__(self, team, player, ipc, ip="127.0.0.1", port=3100):

        self.debug = Scope("Simulationsbridge")
        self.motors = {}
        self.ipc = ipc
        for i in range(1, 21):
            self.motors[i] = MX28(i)
        self.motors[200] = CM730(200)
        self.readregisters = {}
        self.handles= []
        vrep.simxFinish(-1)
        self.clientID=vrep.simxStart(ip,19999,True,True,5000,5)
        self.initHandles()
        #self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.connect((ip, port))
        #self.send("(init (unum %d)(teamname %s))" % (player, team))
        #self.send("(scene rsg/agent/darwin/bitbots.rsg)")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 65123))
        gevent.spawn(self.reciver)


    def initHandles(self):
        error , HeadPan = vrep.simxGetObjectHandle(self.clientID,'j_pan',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , HeadTilt = vrep.simxGetObjectHandle(self.clientID,'j_tilt',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , LHipYaw = vrep.simxGetObjectHandle(self.clientID,'j_pelvis_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error ,  LHipRoll= vrep.simxGetObjectHandle(self.clientID,'j_thigh1_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , LHipPitch = vrep.simxGetObjectHandle(self.clientID,'j_thigh2_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , LKnee = vrep.simxGetObjectHandle(self.clientID,'j_tibia_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , LAnklePitch = vrep.simxGetObjectHandle(self.clientID,'j_ankle1_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , LAnkleRoll = vrep.simxGetObjectHandle(self.clientID,'j_ankle2_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error ,  RHipYaw  = vrep.simxGetObjectHandle(self.clientID,'j_pelvis_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , RHipRoll = vrep.simxGetObjectHandle(self.clientID,'j_thigh1_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , RHipPitch = vrep.simxGetObjectHandle(self.clientID,'j_thigh2_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , RKnee = vrep.simxGetObjectHandle(self.clientID,'j_tibia_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , RAnklePitch = vrep.simxGetObjectHandle(self.clientID,'j_ankle1_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , RAnkleRoll = vrep.simxGetObjectHandle(self.clientID,'j_ankle2_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , LShoulderPitch = vrep.simxGetObjectHandle(self.clientID,'j_shoulder_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , LShoulderRoll = vrep.simxGetObjectHandle(self.clientID,'j_high_arm_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , LElbow = vrep.simxGetObjectHandle(self.clientID,'j_low_arm_l',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , RShoulderPitch = vrep.simxGetObjectHandle(self.clientID,'j_shoulder_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , RShoulderRoll = vrep.simxGetObjectHandle(self.clientID,'j_high_arm_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        error , RElbow = vrep.simxGetObjectHandle(self.clientID,'j_low_arm_r',vrep.simx_opmode_oneshot_wait)
        if error != vrep.simx_return_ok:
            raise SystemError("er konnte ein Handle nicht richtig finden")
        #error , self.vision = vrep.simxGetObjectHandle(self.clientID,'Vision_sensor',vrep.simx_opmode_oneshot_wait)
        #if error != vrep.simx_return_ok:
        #    raise SystemError("er konnte ein Handle nicht richtig finden")
        self.handles = [RShoulderPitch,LShoulderPitch,RShoulderRoll,LShoulderRoll,RElbow,LElbow,RHipYaw,LHipYaw,RHipRoll,LHipRoll,RHipPitch,LHipPitch,RKnee,LKnee,RAnklePitch,LAnklePitch,RAnkleRoll,LAnkleRoll,HeadPan,HeadTilt]

    def read(self, amount):
        """ Ließt bytes aus der seriellen Schnittstelle """
        #cdef bytes
        #data = b"\x00" * amount
        #self.read_ptr(<uint8_t*><char*>data, amount)
        data = ""
        if self.readregisters:
            # wenn nichts zum lesen angemeldet wurde soll wohl keine antwort
            for motor in self.readregisters:
                if motor in self.motors:
                    data2 = ""  # für einfacheres berecnen der chacksumme
                    data += chr(0xFF) + chr(0xFF)
                    data2 += chr(motor)  # motorid
                    data2 += chr(self.readregisters[motor][1] + 2)  # length
                    data2 += chr(0)  # errorbits
                    data2 += self.motors[motor].get_chr_registers(
                            self.readregisters[motor])
                    data += data2 + chr(
                        ~sum([ord(x) for x in data2]) & 0xFF)
                        #daten + checksumme
            if len(data) != amount:
                self.debug("Nicht genug Daten:" +
                    " Die generierte Antwort ist zu kurz!")
                raise IOError("Reading from \"serial\" interface: " +
                    "Not enough data (%d/%d)" % (len(data), amount))
        else:
            self.debug("Es wurde versucht etwas zu lesen, " +
                "obwohl kein Register angefordert wurde")
            raise IOError("Reading from \"serial\" interface: Not enough data")
        return data

    def write(self, data):
        """ Schreibt einen String in dei "Serialle" Schnittstelle"""
        data = [ord(x) for x in data]
        self.readregisters = {}  # leehr machen damit kein mist passiert
        if data[0] == 0xFF and data[1] == 0xFF:
            length = data[3]
            if data[2] == 0xFe and data[4] == 0x83:  # broadcast / syc write
                startregister = data[5]
                startptr = 7
                datalength = data[6]
                while (startptr + datalength) <= length + 3:
                    cid = data[startptr]
                    registers = data[startptr + 1:startptr + datalength + 1]
                    try:
                        self.motors[cid].write_rigisters(startregister,
                            registers)
                    except KeyError:
                        self.debug("Motor %d konnte nicht geschrieben werden."
                            % cid)
                        pass
                    startptr += datalength + 1
                if len(data[startptr:]) != 1:
                    print len(data[startptr:])
                    print [hex(x) for x in data]
                    raise SystemExit("Error decoding message, wrong length")

            elif data[2] == 0xFe and data[4] == 0x92:  # broadcast / syc read
                # data[5] ist 0x0 das muss so sein (warum weiß keiner)
                start = 6
                while (start + 3) <= len(data):
                    cid = data[start + 1]
                    length = data[start]
                    startregister = data[start + 2]
                    self.readregisters[cid] = (startregister, length)
                    start += 3
            elif data[4] == 0x01:  # ping
                cid = data[2]
                if cid in self.motors:  # den motor gibt es
                    self.readregisters[cid] = (0, 0)  # lehre antwort
            elif data[4] == 0x02:  # read
                cid = data[2]
                startptr = data[5]
                length = data[6]
                self.readregisters[cid] = (startptr, length)
            else:
                raise NotImplementedError("Unbekannte Packetart %s"
                    % hex(data[4]))

        else:
            raise IOError("ERROR in \"serial\" Communication " +
                "(no 0xFFFF at beginning)")

        self.prepare_send_simspark_data()  # TODO: veralgemeinern

    def set_speed(self, speed):
        """ Setzt die Baudrate
        Tut in dieser Implementation nichts da es nicht unterstützt wird"""
        pass

    def send(self, data):
        """
        Sends data to Simspark
        """
        count = len(data)
        count_bin = struct.pack('>I', count)
        data = count_bin + data
        #print "Send Data: ", data
        self.socket.sendall(data)

    def recv(self):
        """
        Recive and interpret Data from Simspark
        """

        for motornummer in range(len(self.handles)):

            error, position = vrep.simxGetJointPosition(self.clientID, self.handles[motornummer],vrep.simx_opmode_oneshot)
            if (motornummer == 0 or motornummer == 2):
                position *= -1
            self.motors[motornummer+1].set_position_rad(position)
           # print position, self.motors[motornummer+1]
        print "blubb"
        '''image = vrep.simxGetVisionSensorImage(self.clientID,self.vision,0,vrep.simx_opmode_buffer)
        print image
        if (image[0] is 0):
            img = np.asarray(image[2],dtype=np.uint8)
            shape = image[1]
            shape.append(3)
            img.shape = shape
            self.image = img
            print img.shape
            ipc.set_image(image[1][0],image[1][1],self.image)
        else:
            self.debug("Error beim Empfangen des Bildes") '''
        size = 128
        data, addr = self.sock.recvfrom(size*size*3) # buffer size is 1024 bytes
        self.image = np.fromstring(data, dtype=np.uint8)
        self.image.shape = (size,size,3)
        ipc.set_image(size,size,self.image)
        print self.image
        gevent.sleep(0)



        '''t = d[1].split(' ')
        x = int(t[1])
        y = int(t[2][:-1])
        array = np.fromstring(d[2][2:].decode("base64"), dtype='uint8')
        self.ipc.set_image(x,y, array)
        array2 = np.reshape(array, (y, x, 3), order='C')
        # TODO: Durchreichen des Bildes!
        self.img = ((x,y), array2)'''

    def reciver(self):
        """
        This method starts an endless reciverloop for the Simspark data.
        """
        while True:
            #vrep.simxGetVisionSensorImage(self.clientID,self.vision,0,vrep.simx_opmode_streaming_split+4000)
            self.recv()

    def prepare_send_simspark_data(self):
        """
        This method prepares and sends the Date to Simspark
        """
        for m in range(len(self.handles)):
            #print motor
            motor = self.motors[m+1]
            position = motor.get_vrep_goal()
            if m == 0 or m == 2:
                position *= -1
            vrep.simxSetJointTargetPosition(self.clientID , self.handles[m],
                position,vrep.simx_opmode_oneshot)
            #print motor.get_vrep_goal(), motor
        gevent.sleep(0)




if __name__ == "__main__":
    s = Simulatorbridge("BitBots", 0 ,None, ip="192.168.0.228")
    """while True:
        #s.prepare_send_simspark_data()
        #print s.recv()
        #s.motors[13].set_goal((math.sin(time.time()) * 50) -50)"""
    """m = MX28(1)
    m.set_position(0)
    print 0, m.get_position(), m.get_position_angel()
    m.set_position(-180)
    print -180, m.get_position(), m.get_position_angel()
    m.set_position(180)
    print 180, m.get_position(), m.get_position_angel()
    m.set_position(95)
    print 95, m.get_position(), m.get_position_angel()
    m.set_position(-95)
    print -95, m.get_position(), m.get_position_angel()
    s.motors[2].data[30] = 0 & 0xFF
    s.motors[2].data[31] = (0 >> 8) & 0xFF
    for i in range(0,100):
        print i, s.motors[2], s.motors[2].get_goal(), s.motors[2].get_position(), s.motors[2].get_simspark_value()
        s.prepare_send_simspark_data()
        gevent.sleep(0.1)"""
    print s.motors[1]
    s.motors[1].set_goal(1)
    for i in range(250):
        print s.motors[1], s.motors[1].get_goal(), s.motors[1].get_position(), s.motors[1].get_simspark_value()
        s.prepare_send_simspark_data()
        gevent.sleep(0.05)
        if i == 100:
            s.motors[1].set_goal(4095)
