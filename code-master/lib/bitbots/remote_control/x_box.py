class XBox(object):
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
        self.state5 = 0
        self.state6 = 0
        self.state7 = 0
        self.state8 = 0
        self.state9 = 0
        self.state10 = 0
        self.state11 = 0
        self.state12 = 0

    def wait_get_event(self):
        tmp = self.dev.read(8)
        self.state1 = ord(tmp[0])
        self.state2 = ord(tmp[1])
        self.state3 = ord(tmp[2])
        self.state4 = ord(tmp[3])
        self.state5 = ord(tmp[4])
        self.state6 = ord(tmp[5])
        self.state7 = ord(tmp[6])
        self.state8 = ord(tmp[7])
        #self.state9 = ord(tmp[8])
        #self.state10 = ord(tmp[9])
        #self.state11 = ord(tmp[10])
        #self.state12 = ord(tmp[11])
        if self.state8 != 2:
            print "Falscher Mode vom Controller"

    def print_event(self):
        print "%02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x" % (
            (self.state1),
            (self.state2),
            (self.state3),
            (self.state4),
            (self.state5),
            (self.state6),
            (self.state7),
            (self.state8),
            (self.state9),
            (self.state10),
            (self.state11),
            (self.state12))

    def forward_l(self):
        if self.state3 < 0x80 - 5:  # 5 tolleranz
            return 0x80 - self.state3
        else:
            return 0

    def backward_l(self):
        if self.state3 > 0x80 + 5:  # 5 tolleranz
            return self.state3 - 0x80
        else:
            return 0

    def left_l(self):
        if self.state2 < 0x80 - 5:  # 5 tolleranz
            return 0x80 - self.state2
        else:
            return 0

    def right_l(self):
        if self.state2 > 0x80 + 5:  # 5 tolleranz
            return self.state2 - 0x80
        else:
            return 0

    def forward_r(self):
        if self.state5 < 0x80 - 5:  # 5 tolleranz
            return 0x80 - self.state3
        else:
            return 0

    def backward_r(self):
        if self.state5 > 0x80 + 5:  # 5 tolleranz
            return self.state3 - 0x80
        else:
            return 0

    def left_r(self):
        if self.state4 < 0x80 - 5:  # 5 tolleranz
            return 0x80 - self.state3
        else:
            return 0

    def right_r(self):
        if self.state4 > 0x80 + 5:  # 5 tolleranz
            return self.state3 - 0x80
        else:
            return 0

    def btn5(self):
        return (self.state7 >> 0) & 0x1

    def btn7(self):
        return (self.state7 >> 2) & 0x1


if __name__ == '__main__':
    mouse = XBox()
    while True:
        mouse.print_event()
        mouse.wait_get_event()

