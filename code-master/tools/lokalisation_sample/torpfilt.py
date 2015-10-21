# ------------------------------------------------------------------------
# coding=utf-8
# ------------------------------------------------------------------------
#
#  Created by Martin J. Laubach on 2011-11-15
#
# ------------------------------------------------------------------------

from __future__ import absolute_import

import random
import math
import bisect

from draw import Maze

"""
# Smaller maze

maze_data = ( ( 2, 0, 1, 0, 0 ),
              ( 0, 0, 0, 0, 1 ),
              ( 1, 1, 1, 0, 0 ),
              ( 1, 0, 0, 0, 0 ),
              ( 0, 0, 2, 0, 1 ))
"""

# 0 - empty square
# 1 - occupied square
# 2 - occupied square with a beacon at each corner, detectable by the robot


fix_goal_posts_1 = [0, 27.5]
fix_goal_posts_2 = [0, 12.5]

fix_goal_posts_3 = [60, 27.5]
fix_goal_posts_4 = [60, 12.5]


maze_data = ( ( 1, 1, 0, 0, 2, 0, 0, 0, 0, 1 ),
              ( 1, 2, 0, 0, 1, 1, 0, 0, 0, 0 ),
              ( 0, 1, 1, 0, 0, 0, 0, 1, 0, 1 ),
              ( 0, 0, 0, 0, 1, 0, 0, 1, 1, 2 ),
              ( 1, 1, 0, 1, 1, 2, 0, 0, 1, 0 ),
              ( 1, 1, 1, 0, 1, 1, 1, 0, 2, 0 ),
              ( 2, 0, 0, 0, 0, 0, 0, 0, 0, 0 ),
              ( 1, 2, 0, 1, 1, 1, 1, 0, 0, 0 ),
              ( 0, 0, 0, 0, 1, 0, 0, 0, 1, 0 ),
              ( 0, 0, 1, 0, 0, 2, 1, 1, 1, 0 ))

maze_data = [[0 for j in range(60)] for i in range(40)]

for i in range(40):
    for j in range(60):
        if i == 0 or i == 39 or j == 0 or j == 59:
            maze_data[i][j] = 1


PARTICLE_COUNT = 1500    # Total number of particles

ROBOT_HAS_COMPASS = False # Does the robot know where north is? If so, it
# makes orientation a lot easier since it knows which direction it is facing.
# If not -- and that is really fascinating -- the particle filter can work
# out its heading too, it just takes more particles and more time. Try this
# with 3000+ particles, it obviously needs lots more hypotheses as a particle
# now has to correctly match not only the position but also the heading.

# ------------------------------------------------------------------------
# Some utility functions

def add_noise(level, *coords):
    return [x + random.uniform(-level, level) for x in coords]

def add_little_noise(*coords):
    return add_noise(0.02, *coords)

def add_some_noise(*coords):
    return add_noise(0.1, *coords)

def add_noise2(lst):
    for i in range(len(lst)):
        lst[i] += (random.random()-0.5)*2
    return lst

# This is just a gaussian kernel I pulled out of my hat, to transform
# values near to robbie's measurement => 1, further away => 0
sigma2 = 0.9 ** 2
def w_gauss(a, b):
    p1a, p2a = a
    p1b, p2b = b

    error = (p1a[0] - p1b[0])**2 + (p1a[1] - p1b[1])**2
    error += (p2a[0] - p2b[0])**2 + (p2a[1] - p2b[1])**2
    g = math.e ** -(error ** 2 / (2 * sigma2))
    return g

# ------------------------------------------------------------------------
def compute_mean_point(particles):
    """
    Compute the mean for all particles that have a reasonably good weight.
    This is not part of the particle filter algorithm but rather an
    addition to show the "best belief" for current position.
    """

    m_x, m_y, m_count = 0, 0, 0
    for p in particles:
        m_count += p.w
        m_x += p.x * p.w
        m_y += p.y * p.w

    if m_count == 0:
        return -1, -1, False

    m_x /= m_count
    m_y /= m_count

    # Now compute how good that mean is -- check how many particles
    # actually are in the immediate vicinity
    m_count = 0
    for p in particles:
        if world.distance(p.x, p.y, m_x, m_y) < 1:
            m_count += 1

    return m_x, m_y, m_count > PARTICLE_COUNT * 0.95

# ------------------------------------------------------------------------
class WeightedDistribution(object):
    def __init__(self, state):
        accum = 0.0
        self.state = [p for p in state if p.w > 0]
        self.distribution = []
        for x in self.state:
            accum += x.w
            self.distribution.append(accum)

    def pick(self):
        try:
            return self.state[bisect.bisect_left(self.distribution, random.uniform(0, 1))]
        except IndexError:
            # Happens when all particles are improbable w=0
            return None



def point_inside_polygon(x,y,poly):

    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

# ------------------------------------------------------------------------
class Particle(object):
    def __init__(self, x, y, heading=None, w=1, noisy=False):
        if heading is None:
            heading = random.uniform(0, 360)
        if noisy:
            x, y, heading = add_some_noise(x, y, heading)

        self.x = x
        self.y = y
        self.h = heading
        self.w = w

    def __repr__(self):
        return "(%f, %f, w=%f)" % (self.x, self.y, self.w)

    @property
    def xy(self):
        return self.x, self.y

    @property
    def xyh(self):
        return self.x, self.y, self.h

    @classmethod
    def create_random(cls, count, maze):
        return [cls(*maze.random_free_place()) for _ in range(0, count)]

    def read_sensor(self, maze):
        fact = 80

        h = 90 - self.h

        draw_heading_left = (h + 42.5) % 360
        draw_heading_right = (h - 42.5) % 360

        xL, yL = self.x + math.cos(math.pi*2*draw_heading_left/360.0)*fact, self.y + math.sin(math.pi*2*draw_heading_left/360.0)*fact
        xR, yR = self.x + math.cos(math.pi*2*draw_heading_right/360.0)*fact, self.y + math.sin(math.pi*2*draw_heading_right/360.0)*fact

        poly = [(xL, yL), (xR, yR), (self.x, self.y)]

        seeGoalP1 = point_inside_polygon(fix_goal_posts_1[0], fix_goal_posts_1[1], poly)
        seeGoalP2 = point_inside_polygon(fix_goal_posts_2[0], fix_goal_posts_2[1], poly)
        seeGoalP3 = point_inside_polygon(fix_goal_posts_3[0], fix_goal_posts_3[1], poly)
        seeGoalP4 = point_inside_polygon(fix_goal_posts_4[0], fix_goal_posts_4[1], poly)

        print seeGoalP1, seeGoalP2, seeGoalP3, seeGoalP4

        if seeGoalP1 and seeGoalP2:
            return [fix_goal_posts_1[0] - self.x, fix_goal_posts_1[1] - self.y], [fix_goal_posts_2[0] - self.x, fix_goal_posts_2[1] - self.y]
        elif seeGoalP3 and seeGoalP4:
            return [fix_goal_posts_3[0] - self.x, fix_goal_posts_3[1] - self.y], [fix_goal_posts_4[0] - self.x, fix_goal_posts_4[1] - self.y]
        else:
            return None

    def advance_by(self, speed, checker=None, noisy=False):
        h = self.h
        if noisy:
            speed, h = add_little_noise(speed, h)
            h += random.uniform(-10, 10) # needs more noise to disperse better
        r = math.radians(h)
        dx = math.sin(r) * speed
        dy = math.cos(r) * speed
        if checker is None or checker(self, dx, dy):
            self.move_by(dx, dy)
            return True
        return False

    def move_by(self, x, y):
        self.x += x
        self.y += y

# ------------------------------------------------------------------------
class Robot(Particle):
    speed = 0.2

    def __init__(self, maze):
        super(Robot, self).__init__(*maze.random_free_place(), heading=90)
        self.chose_random_direction()
        self.step_count = 0

    def chose_random_direction(self):
        heading = random.uniform(0, 360)
        self.h = heading

    def read_sensor(self, maze):
        """
        Poor robot, it's sensors are noisy and pretty strange,
        it only can measure the distance to the nearest beacon(!)
        and is not very accurate at that too!
        """
        fact = 80

        h = 90 - self.h

        draw_heading_left = (h + 42.5) % 360
        draw_heading_right = (h - 42.5) % 360

        xL, yL = self.x + math.cos(math.pi*2*draw_heading_left/360.0)*fact, self.y + math.sin(math.pi*2*draw_heading_left/360.0)*fact
        xR, yR = self.x + math.cos(math.pi*2*draw_heading_right/360.0)*fact, self.y + math.sin(math.pi*2*draw_heading_right/360.0)*fact

        poly = [(xL, yL), (xR, yR), (self.x, self.y)]

        seeGoalP1 = point_inside_polygon(fix_goal_posts_1[0], fix_goal_posts_1[1], poly)
        seeGoalP2 = point_inside_polygon(fix_goal_posts_2[0], fix_goal_posts_2[1], poly)
        seeGoalP3 = point_inside_polygon(fix_goal_posts_3[0], fix_goal_posts_3[1], poly)
        seeGoalP4 = point_inside_polygon(fix_goal_posts_4[0], fix_goal_posts_4[1], poly)

        print seeGoalP1, seeGoalP2, seeGoalP3, seeGoalP4

        if seeGoalP1 and seeGoalP2:
            return [fix_goal_posts_1[0] - self.x, fix_goal_posts_1[1] - self.y], [fix_goal_posts_2[0] - self.x, fix_goal_posts_2[1] - self.y]
        elif seeGoalP3 and seeGoalP4:
            return [fix_goal_posts_3[0] - self.x, fix_goal_posts_3[1] - self.y], [fix_goal_posts_4[0] - self.x, fix_goal_posts_4[1] - self.y]
        else:
            return None


    def move(self, maze):
        """
        Move the robot. Note that the movement is stochastic too.
        """
        while True:
            self.step_count += 1
            if self.advance_by(self.speed, noisy=True,
                checker=lambda r, dx, dy: maze.is_free(r.x+dx, r.y+dy)):
                break
            # Bumped into something or too long in same direction,
            # chose random new direction
            self.chose_random_direction()

# ------------------------------------------------------------------------

world = Maze(maze_data)
world.draw()

# initial distribution assigns each particle an equal probability
particles = Particle.create_random(PARTICLE_COUNT, world)
robbie = Robot(world)

while True:
    # Read robbie's sensor
    r_d = robbie.read_sensor(world)

    if r_d is not None:

        # Update particle weight according to how good every particle matches
        # robbie's sensor reading
        for p in particles:
            if world.is_free(*p.xy):
                p_d = p.read_sensor(world)
                if p_d is not None:
                    p.w = w_gauss(r_d, p_d)
                else:
                    p.w = 0
            else:
                p.w = 0

        # ---------- Try to find current best estimate for display ----------
        m_x, m_y, m_confident = compute_mean_point(particles)

        # ---------- Show current state ----------
        world.show_mean(m_x, m_y, m_confident)



        # ---------- Shuffle particles ----------
        new_particles = []

        # Normalise weights
        nu = sum(p.w for p in particles)
        if nu:
            for p in particles:
                p.w = p.w / nu

        # create a weighted distribution, for fast picking
        dist = WeightedDistribution(particles)

        for _ in particles:
            p = dist.pick()
            if p is None:  # No pick b/c all totally improbable
                new_particle = Particle.create_random(1, world)[0]
            else:
                new_particle = Particle(p.x, p.y,
                        heading=robbie.h if ROBOT_HAS_COMPASS else p.h,
                        noisy=True)
            new_particles.append(new_particle)

        particles = new_particles


    world.show_particles(particles)
    world.show_robot(robbie)

    world.show_goal_posts([fix_goal_posts_1,
                           fix_goal_posts_2,
                           fix_goal_posts_3,
                           fix_goal_posts_4])

    # ---------- Move things ----------
    old_heading = robbie.h
    robbie.h += 4
    d_h = robbie.h - old_heading

    # Move particles according to my belief of movement (this may
    # be different than the real movement, but it's all I got)
    for p in particles:
        p.h += d_h # in case robot changed heading, swirl particle heading too
        #p.advance_by(robbie.speed)
