#-*- coding:utf-8 -*-
"""
HorizonParticleFilter
^^^^^^^^^^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 8/16/14: Created (sheepy)

Ein Modul, welches testweise zeigen soll, das bei den entfernungen zum horizont,  vorne, links (90°) und rechts (90°)
dazu geeignet sind die position udn orientierung des roboters ehrauszufinden

"""

import random
import math
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from Particle import FeaturedParticle
from WeightedDistribution import WeightedDistribution
from utils import w_gauss
from utils import add_noise_to_particle, compute_mean_point, get_particle_intersect_point

PARTICLE_COUNT = 1000


class HorizonParticleFilter(object):

    def __init__(self):

        self.robot = FeaturedParticle(0, 0, 0)

        self.particles = [FeaturedParticle(random.randint(-3000, 3000), random.randint(-4500, 4500), random.randint(0, 360)) for i in range(PARTICLE_COUNT)]

    def algorithm_run(self):

        ROUNDS = 100

        for iteration in range(ROUNDS):

            # Calculate what the robot is sensing with noise
            self.calculate_distances_for_defined_particle(self.robot, noise=100)

            # Calculate what the particles are sensing
            for p in self.particles:
                self.calculate_distances_for_defined_particle(p)

            # Calculate the Similarity between Particles and Robots Sensing and assign weight based on that
            self.calculate_similarity_and_assign_weight()

            # Normalize the Weight of the Particles
            self.normalize_particles(self.particles)

            # Analyze some data in each Step
            orientations = [p.orientation for p in self.particles]
            orientations_average = float(sum(orientations)) / len(orientations)
            orientation_std_deviation = sum([(orientations_average - o)**2 for o in orientations]) / len(orientations)

            print "Iteration Step", iteration
            print "Orienation Average/StdDev", orientations_average, orientation_std_deviation
            print "Orientation Robot", self.robot.orientation
            mx, my, mconfidence = compute_mean_point(self.particles, surrounding=250)
            print "PointCount within Surrounding Range:", mconfidence
            print "Robot calc position", int(mx), int(my)
            print "Robot real position", self.robot.x, self.robot.y

            self.plot_some_data(iteration)

            # Generate new Particles based on the Weighted Distribution
            self.particles = self.make_new_particle_cloud(self.particles)

            # Simulate the movement of the Robot and update all particles too
            #self.simulate_robot_movement()

    def simulate_robot_movement(self):
        dx = random.randint(-100, 100)
        dy = random.randint(-100, 100)
        do = random.randint(-15, 15)

        self.robot.x += dx
        self.robot.y += dy
        self.robot.orientation += do

        for p in self.particles:
            p.x += dx
            p.y += dy
            p.orientation += do


    def plot_some_data(self, iteration):

        if iteration % 5 == 0:

            plt.figure(0)

            xpall = [p.x for p in self.particles]
            ypall = [p.y for p in self.particles]

            mx, my, mconfidence = compute_mean_point(self.particles, surrounding=250)

            plt.plot(xpall, ypall, 'yo')
            plt.plot(self.robot.x, self.robot.y, 'rD')
            plt.plot(mx, my, 'cD')

            plt.xlim([-5000, 5000])
            plt.ylim([-5000, 5000])


            plt.axis('equal')
            plt.axhline(y=-4500)
            plt.axhline(y=4500)
            plt.axvline(x=3000)
            plt.axvline(x=-3000)

            orientation = [p.orientation for p in self.particles]

            # A Histogram over all the Orientations of the Particles
            plt.figure(1)
            plt.hist(orientation, 50, normed=1, facecolor='green', alpha=0.75)

            plt.show()


    def normalize_particles(self, particles):
        # Normalise weights
        nu = sum(p.w for p in particles)
        if nu:
            for p in particles:
                p.w = p.w / nu

    def calculate_similarity_and_assign_weight(self):

        for particle in self.particles:


            error_front = abs(self.robot.features[0] - particle.features[0])
            error_left = abs(self.robot.features[1] - particle.features[1])
            error_right = abs(self.robot.features[2] - particle.features[2])

            total = (error_front + error_left + error_right) / 3.0

            similarity1 = w_gauss(error_front, 0, sigma2=1000)
            similarity2 = w_gauss(error_left, 0, sigma2=1000)
            similarity3 = w_gauss(error_right, 0, sigma2=1000)

            similarity = [similarity1, similarity2, similarity3]

            similarity_other = w_gauss(total, 0, sigma2=20000)

            value_to_use = similarity_other

            if value_to_use > 0.5:
                particle.w = value_to_use
            else:
                particle.w = 0

    def distance_to_intersect_point(self, particle, point):
        return math.sqrt((particle.x - point[0])**2 + (particle.y - point[1])**2)

    def calculate_distances_for_defined_particle(self, particle, noise=None):

        p_front = get_particle_intersect_point(particle, angle_offset=0)
        p_left = get_particle_intersect_point(particle, angle_offset=90)
        p_right = get_particle_intersect_point(particle, angle_offset=-90)

        dst_front = self.distance_to_intersect_point(particle, p_front)
        dst_left = self.distance_to_intersect_point(particle, p_left)
        dst_right = self.distance_to_intersect_point(particle, p_right)

        if noise:
            particle.add_feature(0, random.gauss(dst_front, noise))
            particle.add_feature(1, random.gauss(dst_left, noise))
            particle.add_feature(2, random.gauss(dst_right, noise))
        else:
            particle.add_feature(0, dst_front)
            particle.add_feature(1, dst_left)
            particle.add_feature(2, dst_right)

    def make_new_particle_cloud(self, particles):
        wd = WeightedDistribution(particles)
        newparticles = []
        while len(newparticles) < PARTICLE_COUNT:
            picked = wd.pick()
            if picked is None:
                picked = FeaturedParticle(random.randint(-3000, 3000), random.randint(-4500, 4500), random.randint(0, 360))
            else:
                picked = FeaturedParticle(picked.x, picked.y, picked.orientation)
            add_noise_to_particle(picked)
            newparticles.append(picked)
        return newparticles


angle_matching = HorizonParticleFilter()
angle_matching.algorithm_run()