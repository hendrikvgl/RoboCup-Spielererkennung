import math
import random
import matplotlib

matplotlib.interactive(True)
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt



class Visualizer(object):

    def __init__(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, axisbg='green')


        self.X, self.Y = [random.random(),random.random()], [random.random(),random.random()]

        self.surf = self.ax.plot(self.X, self.Y )
        plt.draw() #maybe you want to see this frame?
        plt.show()

    def draw_robot( self, robot ):

        x_t = robot.xy[0] + math.cos(2*math.pi*robot.orientation/360)*300
        y_t = robot.xy[1] + math.sin(2*math.pi*robot.orientation/360)*300

        self.surf = self.ax.plot(robot.xy[0], robot.xy[1], 'ks', markersize=10)
        self.surf = self.ax.plot([robot.xy[0], x_t], [robot.xy[1], y_t], 'k-', markersize=10)

        self.ax.text(robot.xy[0]-30, robot.xy[1]-80, str(robot.name), color='white')

    def clear(self):
        self.ax.cla()

    def draw(self):
        self.ax.set_xlim([-5000, 5000])
        self.ax.set_ylim([-5000, 5000])
        plt.draw()

    def plot_field(self):
        self.ax.plot([0, 0], [-3000, 3000], 'w-')
        self.ax.plot([4500, 4500], [-3000, 3000],'w-')
        self.ax.plot([-4500, -4500], [-3000, 3000], 'w-')
        self.ax.plot([-4500, 4500], [-3000, -3000], 'w-')
        self.ax.plot([-4500, 4500], [3000,  3000], 'w-')
        radius = 700

        self.ax.plot([math.cos(math.pi*2*x/360.0)*radius for x in range(0, 360, 10)], [math.sin(math.pi*2*x/360.0)*radius for x in range(0, 360, 10)], 'w-')


    def draw_ball(self, ball):
        px, py, vx, vy = ball
        self.ax.plot(px, py, 'ro',  markersize=10)
