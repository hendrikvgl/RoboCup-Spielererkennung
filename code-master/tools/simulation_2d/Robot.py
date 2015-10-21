
class Robot(object):

    def __init__(self, name, xy, orientation):
        self.name = name
        self.xy = xy
        self.orientation = orientation
        self.forward = 0
        self.sideward = 0
        self.angular = 0

        self.forward_multiplicator = 60
        self.sideward_multiplicator = 90
        self.angular_multiplicator = 2

