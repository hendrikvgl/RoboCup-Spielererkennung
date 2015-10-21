import math
from settings import *


class PotentialField(object):
    def __init__(self, attract):
        self.vector = [0, 0]
        self.attract = attract

    def update(self, ob):
        obx = ob[0]
        oby = ob[1]
        if obx != 0 or oby != 0:
            dist = math.sqrt(obx ** 2 + oby ** 2)
            obx /= dist
            oby /= dist
            force = 800.0 / dist
            if not self.attract:
                force **= 2

                # self.vector[0] = math.copysign(1/obx**2, obx) * force
                # self.vector[1] = -math.copysign(1/oby**2, oby) * force

                self.vector[0] = -obx * force * 5.0
                self.vector[1] = -oby * force * 5.0
            else:
                # constant attractor
                self.vector[0] = -obx
                self.vector[1] = -oby

                if p_activated_attractors:
                    self.vector[0] *= -80.0
                    self.vector[1] *= -80.0
                else:
                    self.vector = [0, 0]


class PotentialMap(object):
    """
    Definiert die Potential Fields
    """

    def __init__(self, (nr_r, nr_a)):
        """
        :param nr_r: number of obstacles to build a potential field
        """

        self.fields = []
        for i in range(nr_r):
            self.fields.append(PotentialField(False))

        for i2 in range(nr_a):
            self.fields.append(PotentialField(True))

    def compute(self, oblist):
        """
        :return the 3-Tupel vektor
        """
        x = 0
        for field in self.fields:
            field.update(oblist[x])
            x += 1

        vectorx, vectory = (0, 0)

        for field in self.fields:
            if p_ball_repulsor and field == self.fields[-2]:
                #its a ball repulsor, reduced force
                vectorx += field.vector[0] / 5.0
                vectory += field.vector[1] / 5.0

            else:
                vectorx += field.vector[0]
                vectory += field.vector[1]
        vectory /= len(self.fields)
        vectorx /= len(self.fields)

        if p_potential_field_turn:
            forw = vectorx
            fs = -1 if vectorx < 0 else 1
            turn = vectory * fs
            side = 0 # vectory
        else:
            forw = vectorx
            turn = 0
            side = vectory
        #print side

        return forw, turn, side
