class Mouse(object):
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

    def wait_get_event(self):
        tmp = self.dev.read(6)
        self.state1 = ord(tmp[0])
        self.state2 = ord(tmp[1])
        self.state3 = ord(tmp[2])
        self.state4 = ord(tmp[3])
        self.state5 = ord(tmp[4])
        self.state6 = ord(tmp[5])

    def print_event(self):
        print "%s %s %s %s %s %s" % (
            hex(self.state1),
            hex(self.state2),
            hex(self.state3),
            hex(self.state4),
            hex(self.state5),
            hex(self.state6))

    def is_left_button(self):
        return (self.state1 >> 0 & 0x1) == 1

    def is_right_button(self):
        return (self.state1 >> 1 & 0x1) == 1

    def is_middle_button(self):
        return (self.state1 >> 2 & 0x1) == 1

    def is_up_button(self):
        return (self.state1 >> 3 & 0x1) == 1

    def is_down_button(self):
        return (self.state1 >> 4 & 0x1) == 1

    def is_scrol_up(self):
        return (
            (self.state5 >> 0 & 0x1) == 1 and
            (self.state5 >> 7 & 0x1) != 1)

    def is_scrol_down(self):
        return (self.state5 >> 7 & 0x1) == 1

    def move_left(self):
        return (self.state2 >> 4) * -1 + 0xf

    def move_up(self):
        return (self.state3 >> 4) * -1 + 0xf

    def move_right(self):
        return (self.state2 & 0xf)

    def move_down(self):
        return (self.state2 & 0xf)


if __name__ == '__main__':
    mouse = Mouse()
    while True:
        mouse.print_event()
        mouse.wait_get_event()

