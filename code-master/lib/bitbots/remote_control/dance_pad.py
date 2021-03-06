class DancePad(object):
    def __init__(self, dev='/dev/hidraw0'):
        try:
            self.dev = open(dev, 'r')
        except IOError as e:
            if e.errno == 13:
                print "Permission denied on %s" % dev
                print "maybe a 'sudo chmod o+r %s' helps" % dev
                exit(1)
            else:
                raise
        self.state1 = 0
        self.state2 = 0
        self.state3 = 0
        self.state4 = 0

    def wait_get_event(self):
        tmp = self.dev.read(4)
        self.state1 = ord(tmp[0])
        self.state2 = ord(tmp[1])
        self.state3 = ord(tmp[2])
        self.state4 = ord(tmp[3])

    def is_arrow_left(self):
        return (self.state1 >> 0 & 0x1) == 1

    def is_arrow_down(self):
        return (self.state1 >> 1 & 0x1) == 1

    def is_arrow_up(self):
        return (self.state1 >> 2 & 0x1) == 1

    def is_arrow_rigth(self):
        return (self.state1 >> 3 & 0x1) == 1

    def is_dreieck(self):
        return (self.state1 >> 4 & 0x1) == 1

    def is_viereck(self):
        return (self.state1 >> 5 & 0x1) == 1

    def is_x(self):
        return (self.state1 >> 6 & 0x1) == 1

    def is_circle(self):
        return (self.state1 >> 7 & 0x1) == 1

    def is_start(self):
        return (self.state2 >> 0 & 0x1) == 1

    def is_select(self):
        return (self.state2 >> 1 & 0x1) == 1
