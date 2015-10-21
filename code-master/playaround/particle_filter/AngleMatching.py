#-*- coding:utf-8 -*-
"""
AngleMatching
^^^^^^^^^^^^^

.. moduleauthor:: sheepy <sheepy@informatik.uni-hamburg.de>

History:
* 8/10/14: Created (sheepy)

Ein Modul, welches testweise zeigen soll, das bei einem Weltbild, welches an bestimmten positionen um das Feld herum
Markierungen besitzt, die der Roboter zuordnen kann es möglich ist, sowohl seine Position als auch seine Ausrichtung zu
bestimmen.

"""

import random
import math
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from Particle import FeaturedParticle
from WeightedDistribution import WeightedDistribution
from utils import add_noise_to_particle, compute_mean_point

PARTICLE_COUNT = 1000


class DataCollector(object):

    def __init__(self):
        self.data_collection = {}

    def add_data_point(self, key, value):
        if key not in self.data_collection:
            self.data_collection[key] = []
        self.data_collection[key].append(value)

class AngleMatching(object):

    def __init__(self):

        self.robot = FeaturedParticle(0, 3200, 0)

        self.particles = [FeaturedParticle(random.randint(-3000, 3000), random.randint(-4500, 4500), random.randint(0, 360)) for i in range(PARTICLE_COUNT)]

        self.list_of_marks = [
            [-1300, 4500],
            [ 1300, 4500],
            #[-2300, 4500],
            #[ 2300, 4500],

            [-1300, -4500],
            [ 1300, -4500],
            #[-2300, -4500],
            #[ 2300, -4500],
        ]

        self.data_collector = DataCollector()

    def algorithm_run(self):

        ROUNDS = 100

        for iteration in range(ROUNDS):

            # Calculate what the robot is sensing with noise
            self.calculate_angles_for_defined_particle(self.robot, noise=1)

            self.robot.features = {k: v for k,v in self.robot.features.items() if random.random() > 0.1}

            # Calculate what the particles are sensing
            for p in self.particles:
                self.calculate_angles_for_defined_particle(p)

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
            mx, my, mconfidence, mweight = compute_mean_point(self.particles, surrounding=250)
            print "PointCount within Surrounding Range and weight:", mconfidence, mweight
            print "Robot calc position", int(mx), int(my)
            print "Robot real position", self.robot.x, self.robot.y

            print "Distance:", math.sqrt((int(mx) - self.robot.x)**2 + (int(my) - self.robot.y)**2)


            self.plot_some_data(iteration)

            mx, my, mconfidence, mweight= compute_mean_point(self.particles, surrounding=50)
            mweight *= PARTICLE_COUNT
            self.data_collector.add_data_point("NearC", mconfidence)
            self.data_collector.add_data_point("NearW", mweight)

            mx, my, mconfidence, mweight = compute_mean_point(self.particles, surrounding=150)
            mweight *= PARTICLE_COUNT
            self.data_collector.add_data_point("MidC", mconfidence)
            self.data_collector.add_data_point("MidW", mweight)

            mx, my, mconfidence, mweight = compute_mean_point(self.particles, surrounding=350)
            mweight *= PARTICLE_COUNT
            self.data_collector.add_data_point("FarC", mconfidence)
            self.data_collector.add_data_point("FarW", mweight)

            # Generate new Particles based on the Weighted Distribution
            self.particles = self.make_new_particle_cloud(self.particles)

            # Simulate the movement of the Robot and update all particles too
            self.simulate_robot_movement()

        plt.figure(2)
        plt.plot(range(len(self.data_collector.data_collection["NearC"])), self.data_collector.data_collection["NearC"], 'r-')
        plt.plot(range(len(self.data_collector.data_collection["NearW"])), self.data_collector.data_collection["NearW"], 'r-..')
        plt.plot(range(len(self.data_collector.data_collection["MidC"])), self.data_collector.data_collection["MidC"], 'b-')
        plt.plot(range(len(self.data_collector.data_collection["MidW"])), self.data_collector.data_collection["MidW"], 'b-..')
        plt.plot(range(len(self.data_collector.data_collection["FarC"])), self.data_collector.data_collection["FarC"], 'c-')
        plt.plot(range(len(self.data_collector.data_collection["FarW"])), self.data_collector.data_collection["FarW"], 'c-..')

        plt.show()

    def simulate_robot_movement(self):
        dx = random.randint(-40, 40)
        dy = random.randint(-40, 0)
        do = random.randint(-5, 5)

        self.robot.x += dx
        self.robot.y += dy
        self.robot.orientation += do

        #for p in self.particles:
        #    p.x += dx
        #    p.y += dy
        #    p.orientation += do


    def plot_some_data(self, iteration):

        if iteration % 10 == 0:

            plt.figure(0)

            xpall = [p.x for p in self.particles]
            ypall = [p.y for p in self.particles]

            mx, my, mconfidence, mweight = compute_mean_point(self.particles, surrounding=250)

            plt.plot(xpall, ypall, 'yo')
            plt.plot(self.robot.x, self.robot.y, 'rD')
            plt.plot(mx, my, 'cD')

            for i in range(len(self.list_of_marks)):
                plt.plot(self.list_of_marks[i][0], self.list_of_marks[i][1], 'ms')

            plt.xlim([-5000, 5000])
            plt.ylim([-5000, 5000])

            for i in range(len(self.list_of_marks)):
                if i not in self.robot.features:
                    continue

                a, w = self.robot.features[i]
                a += self.robot.orientation
                xl = [self.robot.x+x*math.cos(a*2*math.pi/360) for x in range(10000)]
                yl = [self.robot.y+y*math.sin(a*2*math.pi/360) for y in range(10000)]
                plt.plot(xl, yl, 'g-')

            orientation = [p.orientation for p in self.particles]

            # A Histogram over all the Orientations of the Particles
            plt.figure(1)
            bins = plt.hist(orientation, 50, normed=1, facecolor='green', alpha=0.75)
            print bins[1]

            wlst = [0 for i in range(len(bins[1]))]
            for p in self.particles:
                idx = len([1 for h in bins[1] if p.orientation < h]) -1
                wlst[idx] += p.w
            print "Wlist", wlst
            plt.plot(bins[1], wlst, "rd")
            plt.show()


    def normalize_particles(self, particles):
        # Normalise weights
        nu = sum(p.w for p in particles)
        if nu:
            for p in particles:
                p.w = p.w / nu

    def calculate_similarity_and_assign_weight(self):
        for particle in self.particles:

            similarity_all = []
            total_weight = 0
            for e in range(len(self.list_of_marks)):
                if e not in self.robot.features:
                    continue

                value, weight = particle.features[e]
                total_weight += weight
                cval = ((value*2*math.pi/360 - self.robot.features[e][0]*2*math.pi/360)**2) / (math.pi*2)**2
                similarity_all.append(cval * weight)

            similarity_all = [s/ float(total_weight) for s in similarity_all]

            try:
                error_avrg = sum(similarity_all) / len(similarity_all)
                std_dev = math.sqrt(sum([(s - error_avrg)**2 for s in similarity_all]) / len(similarity_all))

                if std_dev < math.sqrt(0.01):

                    particle.w = 1.0 / error_avrg

                else:
                    particle.w = 0
            except:
                particle.w = 0

    def calculate_angles_for_defined_particle(self, particle, noise=None):

        for i in range(len(self.list_of_marks)):
            marker = self.list_of_marks[i]
            deltax = marker[0] - particle.x
            deltay = marker[1] - particle.y

            r = math.sqrt(deltax**2 + deltay**2)

            deltax /= r
            deltay /= r

            if float(deltax) == 0.0:
                phi = 0
            else:
                phi = math.atan(abs(deltay/float(deltax)))

            if deltax < 0:
                if deltay < 0:
                    phi = math.pi + phi
                else:
                    phi = math.pi - phi

            else:
                if deltay < 0:
                    phi = 2*math.pi - phi

            phi = 360*phi / (2*math.pi)
            phi -= particle.orientation

            if noise is not None:
                phi += random.gauss(0, noise)

            particle.add_feature(i, [phi, random.randint(1,1)])

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


angle_matching = AngleMatching()
angle_matching.algorithm_run()