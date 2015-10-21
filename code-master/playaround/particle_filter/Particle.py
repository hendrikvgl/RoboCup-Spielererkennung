import math


class Particle(object):

    def __init__(self, x, y, orientation, w=1):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.w = w

        self.features = []

    def __repr__(self):
        return "(%f, %f, w=%f)" % (self.x, self.y, self.w)

    @property
    def xy(self):
        return self.x, self.y


class FeaturedParticle(Particle):

    def __init__(self, x, y, orientation, w=1):
        Particle.__init__(self, x, y, orientation, w)

        self.features = {}

    def add_feature(self, key, value):
        self.features[key] = value

    def distance_to(self, other_particle):
        return math.sqrt((self.x - other_particle.x)**2+(self.y - other_particle.y))

    def __repr__(self):
        return "(%f, %f, w=%f) %s" % (self.x, self.y, self.w, "\t".join([str(e[0]) + ": " + str(e[1]) for e in self.features.items()]))
