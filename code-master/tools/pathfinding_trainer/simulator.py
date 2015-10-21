# -*- coding: utf-8 -*-
import os
from potentialmap import PotentialMap
import math
from settings import *
from multiprocessing import Pool


PLOT = p_plot

try:
    import matplotlib
    matplotlib.use("SVG")
    import matplotlib.pyplot as plt

except ImportError:  # If not matplotlib is avilable i.e. in  pypy, no plotting can be activated
    PLOT = False


def rounds((self, net, world)):
    """
    Simulates one Secenario
    :param net:
    :type net: network.Network
    :param world:
    :type world: Worldmodel
    """

    self.counter1 += 1
    br = 1 if p_ball_repulsor else 0
    potential_map = PotentialMap((len(world.obstacles)+br, 1))
    for i in xrange(p_max_steps + 1):
        world.set_local_positions()
        if p_activated_neuronal_net:
            input_value_list = list(world.robot.get_local_positions())
            input_value_list.extend(self.pot_diff)
            forward, turn, side = net.compute(input_value_list)
        else:
            forward, turn, side = 0, 0, 0
        if p_activated_potential_map:
            #add Ball to obstacle list to avoid collison
            brl = [(world.robot.ball_u, world.robot.ball_v)] if p_ball_repulsor else []

            p_list = world.robot.obstacle_list + brl + [(world.robot.ball_u, world.robot.ball_v)]

            vforward, vturn, vside = potential_map.compute(p_list)
            self.pot_diff = [vforward, vturn, vside]
            forward += vforward
            turn += vturn
            side += vside

        forward *= 5
        turn *= 5
        side *= 5
        world.robot.update_input(forward, turn, side)
        world.robot.update_pos()
        world.robot.set_quality()
        if world.is_reached():
            break
    if PLOT and gui.plot:

        gui.plot_path(world.robot.history, world.obstacles, world.ball, world.goalcenter)

        #gui.fig.show()

        #if self.counter1 < 10:
        #    gui.fig.savefig("run" + str(self.counter1))

    if p_debug and self.counter1 % 10 == 0:
        with open("debug/" + p_debug_folder_name + "/simulation.json", "a") as js:
            json.dump([(world.robot.min_dist, world.robot.step_dist_manus, world.robot.go_away_manus),
                       world.robot.history,
                       world.robot.data_history],
                      js)
            js.write("\n")

    i = world.robot.step_dist_manus + world.robot.stands_wrong_manus

    return i


class SimCases(object):
    """
    Defines the different Simulationscenarios
    """

    def __init__(self, number):
        self.cases = []
        if p_random_sim_cases:
            self.create_random_cases(p_cases)
        else:
            inf = float('inf')

            self.cases.append([
                (2000, 1000, 180),  # Robot
                (1000, 1500),  # Ball
                (0, 2000),  # GPC
                [(3400, 1000)],  # obstacle
                (0, inf)  # iteration range
            ])

            self.cases.append([
                (2000, 1000, 180),  # Robot
                (600, 1000),  # Ball
                (0, 2000),  # GPC
                [(1500, 1100), (1500, 900), (1500, 1000), (1520, 1120), (1520, 880)],  # obstacle
                (0, inf)  # iteration range
            ])
            """
            self.cases.append([
                (2000, 1000, 240),  # Robot
                (1000, 1000),  # Ball
                (0, 2000),  # GPC
                [(3400, 1000)],  # obstacle
                (0, inf)  # iteration range
            ])

            self.cases.append([
                (2000, 1000, 300),  # Robot
                (1000, 1000),  # Ball
                (0, 2000),  # GPC
                [(3400, 1000)],  # obstacle
                (0, inf)  # iteration range
            ])

            self.cases.append([
                (2000, 1000, 225),  # Robot
                (1000, 1000),  # Ball
                (0, 2000),  # GPC
                [(3400, 1000)],  # obstacle
                (0, inf)  # iteration range
            ])

            self.cases.append([
                (2000, 1000, 160),  # Robot
                (1000, 1000),  # Ball
                (0, 2000),  # GP2
                [(1400, 1000)],  # obstacle
                (0, inf)  # iteration range
            ])

            self.cases.append([
                (2000, 1000, 200),  # Robot
                (1000, 1000),  # Ball
                (0, 2000),  # GP1
                [(1400, 1000)],  # obstacle
                (0, inf)  # iteration range
            ])

            self.cases.append([
                (3000, 4000, 270),
                (1000, 1000),
                (0, 2000),
                [(1400, 1000)],
                (0, inf)
            ])

            self.cases.append([
                (2000, 1000, 45),
                (1000, 1000),
                (0, 2000),
                [(1400, 1000)],
                (0, inf)
            ])

            self.cases.append([
                (1000, 1000, 0),
                (2000, 3000),
                (0, 2000),
                [(1400, 2000)],
                (0, inf)
            ])
    """
    def add_random_case(self):
        self.cases.pop(0)
        self.cases.pop(0)
        self.cases.append(self.random_case())
        self.cases.append(self.random_case())

    @staticmethod
    def random_case():
        robot = [None, None, None]
        random.seed(p_seed_get())
        robot[0] = random.randint(0, 5000)
        random.seed(p_seed_get())
        robot[1] = random.randint(0, 5000)
        random.seed(p_seed_get())
        robot[2] = random.randint(0, 359)

        ball = [None, None]
        random.seed(p_seed_get())
        ball[0] = random.randint(0, 5000)
        random.seed(p_seed_get())
        ball[1] = random.randint(0, 5000)

        oblist = []
        for n in range(p_nr_obstacles):
            ob = [None, None]
            random.seed(p_seed_get())
            ob[0] = random.randint(0, 5000)
            random.seed(p_seed_get())
            ob[1] = random.randint(0, 5000)
            oblist.append(ob)

        return [robot, ball, (0, 2000), oblist, (0, float('inf'))]

    def create_random_cases(self, nr):
        if nr == 0:
            self.cases = []
            self.cases.append([
                (2000, 3000, 180),
                (1300, 2000),
                (0, 4000),
                [(1500, 1000), (1500, 3000)],
                (0, float('inf'))
            ])
        else:
            self.cases = []
            for c in range(nr):
                self.cases.append(self.random_case())


class GUI(object):
    """
    Takes care of matplotlib
    """

    def __init__(self):
        self.plot = False
        self.fig = plt
        self.fig.figure(1, figsize=(10, 10), dpi=1000, linewidth=3)
        self.plotcount = 0

        self.last = []
        self.last_ball = None
        self.last_obstacles = []

        self.lastpop = []
        self.fig.axis("off")
        self.fig.grid(False)
        self.fig.hold(True)
        #self.fig.plot([-3000, 3000], [0, 0], 'w-')
        #self.fig.plot([-3000, 3000], [4500, 4500], 'w-')
        #self.fig.plot([-3000, 3000], [-4500, -4500], 'w-')
        #self.fig.plot([-3000, -3000], [-4500, 4500], 'w-')
        #self.fig.plot([3000, 3000], [-4500, 4500], 'w-')
        radius = 700
        self.fig.plot([math.cos(math.pi * 2 * x / 360.0) * radius for x in range(0, 360, 10)],
                      [math.sin(math.pi * 2 * x / 360.0) * radius for x in range(0, 360, 10)], 'w-')

    def draw_ball(self, ballx, bally):
        self.fig.figure(1)
        if self.last_ball:
            self.last_ball[0].remove()
        self.last_ball = self.fig.plot(ballx, bally, "ro", markersize=10)

    def draw_goal(self, g1_x, g1_y, g2_x, g2_y):
        self.fig.figure(1)
        self.fig.plot(g1_x, g1_y, "yo", markersize=10)
        self.fig.plot(g2_x, g2_y, "yo", markersize=10)

    def draw_obstacle(self, o1, o2):
        self.fig.figure(1)

        return self.fig.plot(o1, o2, "bo", markersize=10)

    def plot_path(self, p_list, ob, ball_p, goalpost1_p):
        self.fig.figure(1)
        self.fig.interactive(True)

        gui.draw_ball(ball_p.x_poition, ball_p.y_position)
        gui.draw_goal(goalpost1_p.x_poition, goalpost1_p.y_position-1000, goalpost1_p.x_poition, goalpost1_p.y_position+1000)
        for x in gui.last_obstacles:
            x[0].remove()
            gui.last_obstacles = []
        for x in range(len(ob)):
            gui.last_obstacles.append(gui.draw_obstacle(ob[x].x_poition, ob[x].y_position))

        for old in self.last:
            old.remove()
        self.last = []
        self.last.extend(self.fig.plot(p_list[0][0], p_list[0][1], color="r", marker="."))
        if not os.path.exists("bilder/" + p_image_folder):
            os.mkdir("bilder/"+p_image_folder)
        i = 0
        for point in p_list:

            if i % 2 == 0:
                #self.last.extend(self.fig.plot(point[0], point[1], color="b", marker="."))
                xd = 60 * math.cos(math.radians(point[2]))
                yd = 60 * math.sin(math.radians(point[2]))
                self.last.append(self.fig.arrow(point[0], point[1], xd, yd, width=0.2, head_length=20, head_width=25, ec="b"))

                if p_draw_each_step:
                    self.fig.draw()
                    self.fig.savefig("bilder/"+p_image_folder+"/path-" + str("%03i" % self.plotcount) + "_" + str("%03i" % i), facecolor="w")
            i += 1

        for o in range(1 if not p_draw_each_step else 8):
            self.fig.draw()
            self.fig.savefig("bilder/"+p_image_folder+"/path-" + str("%03i" % self.plotcount) + "_" + str("%03i" % i), facecolor="w")
            i += 1

        self.plotcount += 1


    def plot_fitness(self, f_list):
        fitplot = plt
        fitplot.figure(2)
        # fitplot.subplot(212)
        for e in self.lastpop:
            e.remove()
        self.lastpop = []
        self.lastpop.extend(fitplot.plot(f_list))
        #self.plotcount += 1


        # fitplot.draw()
        #fitplot.savefig("population-" + str(self.plotcount))


if PLOT:
    gui = GUI()


class Simulator(object):
    def __init__(self):
        self.simcases = SimCases(None)
        self.counter1 = 0
        self.PLOT = PLOT
        self.pot_diff = [0, 0, 0]
        if PLOT:
            self.gui = gui

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def simulate(self, net, iplot=False):
        """
        Simulates for one Network to gather the fitness
        :param net: the Network to test
        :type net: network.Network
        :param iplot: Says if it shall plot furter informations about the population
        :return: The Fittness
        :rtype: int or float
        """
        if PLOT:
            gui.plot = iplot

        worlds = []
        for case in self.simcases.cases:
            if case[4][0] <= self.counter1 <= case[4][1]:
                caseworld = Worldmodel(case[0], case[1], case[2], case[3])
                worlds.append((self, net, caseworld))

        results = map(rounds, worlds)
        #results = self.pool.map(rounds, worlds)

        result = reduce(lambda x, y: x + y, results)

        if p_random_sim_cases:
            self.simcases.create_random_cases(p_cases)
        return result, net


class Worldmodel(object):
    def __init__(self, robot_p, ball_p, goalpost1_p, ob):
        self.ball = Ball(ball_p[0], ball_p[1])
        self.goalcenter = Goalcenter(goalpost1_p[0], goalpost1_p[1] - 1500)

        self.robot = Robot(robot_p[0], robot_p[1], robot_p[2])
        self.obstacles = []
        for obstacle in ob:
            self.obstacles.append(Obstacle(obstacle[0], obstacle[1]))



    def is_reached(self):
        """
        Returns true if the robot is ready to kick
        """
        return self.robot.in_kick_distance() and self.robot.is_aligned()

    def set_local_positions(self):
        """
        Sets the correct u and v value for the robot
        """
        self.robot.ball_u, self.robot.ball_v = self.uv(self.robot.x_position, self.robot.y_position,
                                                       self.robot.orientation,
                                                       self.ball.x_poition, self.ball.y_position)

        self.robot.goalcenter_u, self.robot.goalcenter_v = self.uv(self.robot.x_position, self.robot.y_position,
                                                                   self.robot.orientation,
                                                                   self.goalcenter.x_poition,
                                                                   self.goalcenter.y_position)

        self.robot.obstacle_list = list()
        for obstacle in self.obstacles:
            self.robot.obstacle_list.append(self.uv(self.robot.x_position, self.robot.y_position,
                                                    self.robot.orientation,
                                                    obstacle.x_poition, obstacle.y_position))

    @staticmethod
    def uv(x, y, ang, xo, yo):
        """
        :param x: x position of the robot
        :param y: y position of the robot
        :param ang: orientation of the robot in degrees
        :param xo: x position of the object
        :param yo: y position of the object
        computes the u and v values based on x,v values
        """
        rad_ang = math.radians(ang)
        u = -(x - xo) * math.cos(rad_ang) + (y - yo) * math.sin(-rad_ang)
        v = (x - xo) * math.sin(rad_ang) - (y - yo) * math.cos(rad_ang)

        return u, v


class Robot(object):
    """
    Model of the tranied Robot
    """

    def __init__(self, x, y, deg):
        self.x_position = x
        self.y_position = y
        self.orientation = deg

        self.real_forward = 0
        self.real_turn = 0
        self.real_side = 0

        self.goal_forward = 0
        self.goal_turn = 0
        self.goal_side = 0

        self.ball_u = 0
        self.ball_v = 0
        self.goalcenter_u = 0
        self.goalcenter_v = 0
        self.obstacle_list = []

        self.history = []
        self.data_history = []
        self.min_dist = 30000
        self.go_away_manus = 0
        self.step_dist_manus = 0
        self.stands_wrong_manus = 3500

        self.startdist = 0

    def get_local_positions(self):
        """
        :return: the current u and v values of objects
        :rtype: tuple
        """
        return (self.ball_u / 1000.0) + p_input_noise(), \
               (self.ball_v / 1000.0) + p_input_noise(), \
               (self.goalcenter_u / 1000.0) + p_input_noise(), \
               (self.goalcenter_v / 1000.0) + p_input_noise()

    def is_aligned(self):
        """
        :return: Is the Robot enogh aligned to the Goal?
        :rtype boolean
        """
        return abs(math.degrees(math.atan2(self.goalcenter_v, self.goalcenter_u))) < 60.0

    def is_slowed_down(self):
        """
        :return: Is the robot slow enough?
        :rtype boolean
        """
        return (abs(self.real_forward) + abs(self.real_side)) < 5

    def set_quality(self):
        """
        Sets the Values of the step for quality purposes
        """
        dist = (self.ball_v ** 2 + self.ball_u ** 2) ** 0.5

        if self.startdist == 0:
            if dist == 0.0:
                self.startdist = 0.1
            else:
                self.startdist = dist

        dist_manus = 180 * dist / self.startdist
        #self.step_dist_manus += dist_manus * (
        #    (len(self.history) * 10.0) / p_max_steps) + 300  # Strafe wenn der roboter weit weg ist
        self.step_dist_manus += 440 + dist_manus

        if dist > self.min_dist:
            self.go_away_manus += p_go_away_manus

        factor = 1 + (len(self.history) / 10.0)
        self.min_dist = min(self.min_dist * factor, dist)

        if dist == 0.0:
            dist = 0.1
        else:
            dist = dist

        if p_align_manus:
            self.stands_wrong_manus += abs(math.atan2(self.goalcenter_v, self.goalcenter_u)) * 85 * (400.0/dist)**1.7

        # zu nah an einem hinderniss langgelaufen
        self.step_dist_manus += reduce(lambda x, y: x+y, map(lambda x: (1/((x[0]**2 + x[1]**2)**0.5 + 0.1)*2000)**2.7, self.obstacle_list))

        self.step_dist_manus += self.too_high_values()
        self.step_dist_manus += self.too_fast_changing()

    def too_fast_changing(self):
        """
        Computes the manus if the values are changing to fast
        :return:
        """
        x = 0
        x += abs(self.goal_turn - self.real_turn) * 3
        x += abs(self.goal_side - self.real_side) * 5
        x += abs(self.goal_forward - self.real_forward) * 1
        return x

    def too_high_values(self):
        """
        Computes the manus for too high values of the movement
        :return:
        """
        x = 0
        x += 0 if abs(self.goal_forward) < 8 else abs(self.goal_forward) * 3
        x += 0 if abs(self.goal_side) < 4 else abs(self.goal_side) * 3
        x += 0 if abs(self.goal_turn) < 7 else abs(self.goal_turn) * 3
        return x

    def in_kick_distance(self):
        """
        :return: is True if the robot ha reaced its goal
        :rtype: bool
        """
        # print self.ball_u, self.ball_v

        return 30.0 < self.ball_u < 290.0 and -120.0 < self.ball_v < 120.0

    def update_input(self, forward, turn, side=0.0):
        """
        Setter für die Geschwindigkeiten
        """
        self.goal_forward = forward
        self.goal_turn = turn
        self.goal_side = side

    def update_pos(self):
        """
        Updates the position on the field based on the current movement
        """
        # update Speed
        self.real_turn = min(max(((self.real_turn * 3 + self.goal_turn) / 5.0), -6.0), 6.0)
        print self.real_turn
        self.real_side = min(max(((self.real_side * 3 + self.goal_side) / 4.0), -3.5), 3.5)

        self.real_forward = min(max(((self.real_forward * 3 + self.goal_forward) / 4.0), -4.0), 5.0) -\
                            abs(self.real_side) / 5.0

        # print "rf: ", self.real_forward, " rs: ", self.real_side, " rt: ", self.real_turn
        #print "gf: ", self.goal_forward, " gs: ", self.goal_side, " gt: ", self.goal_turn

        #update position

        self.history.append((self.x_position, self.y_position, self.orientation))
        self.data_history.append(((self.ball_u, self.ball_v), (self.real_forward, self.real_turn, self.real_side)))

        self.orientation = (self.orientation + (self.real_turn * p_turn_factor)) % 360.0

        self.x_position += self.real_forward * math.cos(math.radians(self.orientation)) * p_move_factor
        self.y_position += self.real_forward * math.sin(math.radians(self.orientation)) * p_move_factor

        self.x_position += self.real_side * math.cos(math.radians((self.orientation + 90)) % 360.0) * p_move_factor
        self.y_position += self.real_side * math.sin(math.radians((self.orientation + 90)) % 360.0) * p_move_factor


class Ball(object):
    """
    A Ball in the Simulation
    """

    def __init__(self, x, y):
        self.x_poition = x
        self.y_position = y


class Goalcenter(object):
    """
    A Goalcenter in in the Simulation
    """

    def __init__(self, x, y):
        self.x_poition = x
        self.y_position = y


class Obstacle(object):
    """
    An obstacle
    """

    def __init__(self, x, y):
        self.x_poition = x
        self.y_position = y
