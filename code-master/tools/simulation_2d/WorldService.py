import random
import socket
import threading
import time
import math

from Robot import Robot
from Visualizer import Visualizer

delta = 0.1

"""
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
"""

class WorldService(threading.Thread):




    def __init__(self):
        threading.Thread.__init__(self)
        # Velocity and Position
        self.ball = [0, 0, 0, 0]
        self.robots = {}
        self.running = False
        self.start_positions = [
            [[random.randint(-4500, 0), random.randint(-3000, 3000)], random.randint(0, 360)],
            [[random.randint(-4500, 0), random.randint(-3000, 3000)], random.randint(0, 360)],
            [[random.randint(-4500, 0), random.randint(-3000, 3000)], random.randint(0, 360)],
            [[random.randint(-4500, 0), random.randint(-3000, 3000)], random.randint(0, 360)],
            [[random.randint(-4500, 0), random.randint(-3000, 3000)], random.randint(0, 360)],
            [[random.randint(-4500, 0), random.randint(-3000, 3000)], random.randint(0, 360)]
        ]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP


    def get_start_position_based_on_count(self):
        length = len(self.robots)
        return self.start_positions[length]

    def register_robot(self, robotname):
        if robotname not in self.robots:
            pos, orient = self.get_start_position_based_on_count()
            self.robots[robotname] = Robot(robotname, pos, orient)
            return True
        else:
            return False

    def has_robot(self, name):
        return name in self.robots.keys()

    def start_main_loop(self):
        self.started = time.time()
        self.deamonized = True
        self.start()

    def set_running(self, value):
        self.running = value
        return True

    def put_ball_to_position(self, x, y):
        """ Puts the ball to a specific position """
        self.ball = (x, y)

    def get_absolute_ball_position(self):
        """ Returns the absolute ball position """
        return self.ball


    def put_robot_to_position(self, robotname, x, y):
        """ Puts the named robot to a specific position """
        pass


    def send_updated_position(self, robot):
        UDP_IP = "127.0.0.1"
        # Hack to test this on one computer
        UDP_PORT = 9050+int(robot.name)

        # The coordinate system is another within the robots perspective
        MESSAGE = str([int(robot.name), robot.xy[0], robot.xy[1], robot.orientation % 360])

        print "message:", MESSAGE

        self.sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


    def get_update_info(self, robotname):
        """ This method calculates the data a robot should get """
        robot = self.robots[robotname]

        robot.orientation %= 360

        rad_orient = (robot.orientation / 360.0) *2 * math.pi

        x, y = robot.xy
        xb, yb, vxb, vyb = self.ball

        distance = math.sqrt((x-xb)**2 + (y-yb)**2)

        delta_x = x - xb
        delta_y = y - yb

        print delta_x
        print delta_y

        u = -delta_x * math.cos(-rad_orient) + delta_y*math.sin(-rad_orient)
        v = delta_x * math.sin(-rad_orient) + delta_y*math.cos(-rad_orient)

        v *= -1

        print u, v, distance
        return u, v, distance

    def update_walking_for(self, player, f, s, a, active):
        assert player in self.robots
        robot = self.robots[player]
        robot.forward = f
        robot.sideward = s
        robot.angular = a
        robot.walk_active = active
        print "Walking:", f, s, a
        return True


    def run(self):
        drawer = Visualizer()
        while True:
            for key in self.robots:
                robot = self.robots[key]
                if self.running:
                    print "update"
                    self.update_robot(robot, delta)
                    self.send_updated_position(robot)
                drawer.draw_robot(robot)
            if self.running:
                self.update_ball()
            drawer.draw_ball(self.ball)
            drawer.plot_field()
            drawer.draw()
            time.sleep(0.1)
            drawer.clear()

    def kick(self, robotname):
        robot = self.robots[robotname]

        xb, yb, vxb, vyb = self.ball

        vxb = 250*math.sin(2*math.pi*robot.orientation/360.0)
        vyb = 250*math.cos(2*math.pi*robot.orientation/360.0)

        self.ball = [xb, yb, vxb, vyb]

        return True

    def kick_ball_side(self, robotname, direction):
        robot = self.robots[robotname]

        xb, yb, vxb, vyb = self.ball

        if direction == "left":
            orient = 60
        elif direction == "right":
            orient = -60
        else:
            orient = 0

        orient = (orient + robot.orientation) % 360

        vxb = 450*math.sin(2*math.pi*orient/360.0)
        vyb = 450*math.cos(2*math.pi*orient/360.0)

        self.ball = [xb, yb, vxb, vyb]

        return True

    def update_robot(self, robot, dt):
        robot.orientation += dt*robot.angular*robot.angular_multiplicator % 360

        robot.xy[0] += (robot.forward*dt*robot.forward_multiplicator)*math.cos(2*math.pi*robot.orientation/360.0)
        robot.xy[1] += (robot.forward*dt*robot.forward_multiplicator)*math.sin(2*math.pi*robot.orientation/360.0)

        if robot.sideward > 0:
            ori = (robot.orientation - 90) % 360
        elif robot.sideward < 0:
            ori = (robot.orientation + 90) % 360
        else:
            ori = 0

        sx = (abs(robot.sideward)*dt*robot.sideward_multiplicator)*math.cos(2*math.pi*ori/360.0)
        sy = (abs(robot.sideward)*dt*robot.sideward_multiplicator)*math.sin(2*math.pi*ori/360.0)

        print ori, sx, sy

        robot.xy[0] += sx
        robot.xy[1] += sy

        print robot.xy

        # sidewards not supported by now

    def update_ball(self):
        px, py, vx, vy = self.ball
        px += vx*delta
        py += vy*delta

        if vx > 0.01:
            vx *= 0.95
        else:
            vx = 0

        if vy > 0.01:
            vy *= 0.95
        else:
            vy = 0

        self.ball = [px, py, vx, vy]