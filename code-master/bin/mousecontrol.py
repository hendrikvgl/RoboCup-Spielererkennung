#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bitbots.remote_control.mouse import Mouse
from bitbots.remote_control.keyboard import KeyBoardControl
from bitbots.debug import Scope

class MouseControl(KeyBoardControl):
    def __init__(self, debug,  dev='/dev/hidraw0'):
        super(MouseControl, self).__init__(debug)
        self.mouse=Mouse(dev)

    def control(self):
        while True:
            self.mouse.wait_get_event()

            if self.mouse.is_left_button():
                self.send('a')
            if self.mouse.is_right_button():
                self.send('d')
            if self.mouse.is_middle_button():
                self.send(' ')
            if self.mouse.is_scrol_up():
                self.send('w')
            if self.mouse.is_scrol_down():
                self.send('s')
            if self.mouse.is_up_button():
                self.send('play lk')
            if self.mouse.is_down_button():
                self.send('play rk')

if __name__ == '__main__':
    debug = Scope("Mousecontrol")
    dev = raw_input("Device vom Dancepad ändern? (default: /dev/hidraw0)")
    if not dev:
        dev = "/dev/hidraw0"
    ctrl = MouseControl(debug, dev)
    ctrl.control()
