import random
from matplotlib.pyplot import plot, show, hist2d, hist, xlim, ylim
from Particle import Particle
from WeightedDistribution import WeightedDistribution
from utils import get_uv_robot_to_robot, w_gauss, get_robot_distance, add_noise_to_particle


class RealRobot(object):

    def __init__(self, name, x, y, orientations):
        self.name = name
        self.x = x
        self.y = y
        self.orientation = orientations


class World(object):

    #         (0, 4500)     #
    #                       #
    #                       #
    #         (0,0)         #
    #---------o-------------#
    #                       #
    #                       #
    #                       #
    #        (0, -4500)     #



    def make_new_particle_cloud(self, PARTICLE_COUNT):
        wd = WeightedDistribution(self.particles)
        newparticles = []
        while len(newparticles) < PARTICLE_COUNT:
            picked = wd.pick()
            if picked is None:
                picked = Particle(random.randint(-3000, 3000), random.randint(-4500, 4500), random.randint(0, 360))
            else:
                picked = Particle(picked.x, picked.y, picked.orientation)
            add_noise_to_particle(picked)
            newparticles.append(picked)
        return newparticles

    def __init__(self):

        PARTICLE_COUNT = 2500

        self.robots = []
        self.robots.append(RealRobot("Goalie", 0, -4500, 90))
        self.robots.append(RealRobot("Fieldie1", 0, -900, 180))
        self.robots.append(RealRobot("Fieldie2", -1200, -1500, 180))
        self.robots.append(RealRobot("Fieldie3", 1200, -2400, 180))

        self.ball = Particle(0, 0, 0)


        print get_uv_robot_to_robot(self.robots[0], self.robots[1])
        print get_uv_robot_to_robot(self.robots[0], self.robots[2])
        print get_uv_robot_to_robot(self.robots[0], self.robots[3])


        self.particles = [Particle(random.randint(-3000, 3000), random.randint(-4500, 4500), random.randint(0,360)) for i in range(PARTICLE_COUNT)]


        for i in range(200):
            self.filter_particles_based_on_measurement()
            self.normalize_particles()
            self.particles = self.make_new_particle_cloud(PARTICLE_COUNT)

            self.ball.x += random.randint(0, 10)
            self.ball.y += random.randint(0, 10)

            if i % 20 == 0:
                particles_x = [p.x for p in self.particles]
                particles_y = [p.y for p in self.particles]

                plot(particles_x, particles_y, 'ro')
                plot([r.x for r in self.robots], [r.y for r in self.robots], "bs")
                xlim([-3000, 3000])
                ylim([-4500, 4500])

                show()


    def normalize_particles(self):
        # Normalise weights
        nu = sum(p.w for p in self.particles)
        if nu:
            for p in self.particles:
                p.w = p.w / nu

    def filter_particles_based_on_measurement(self):
        # Based on Robot 0 get all distances to other robots
        distances = [get_robot_distance(self.robots[0], self.ball)]

        # Iterate over every particle (possible other robot)
        for i in range(len(self.particles)):
            p = self.particles[i]
            # Calculate the Gaussian based on the distance of the particle to the measurements
            gaussians = [w_gauss(d, get_robot_distance(self.robots[0], p), sigma2=500) for d in distances]
            # Assign the new weight to the particle
            self.particles[i].w = max(gaussians)

    def robot_distance_matrix(self):
        d = [[int(get_robot_distance(r1, r2)) for r1 in self.robots] for r2 in self.robots]
        return d


    def gaussian_distance_two_matrices(self, sigma2=100):
        uvs = [get_uv_robot_to_robot(self.robots[0], r1) for r1 in self.robots][1:]


        for particle in self.particles:

            uv = get_uv_robot_to_robot(self.robots[0], particle)

            weights = [self.w_gauss2d(uv, uvelem) for uvelem in uvs]

            weights = [w for w in weights if w[0] > 0 and w[1] > 0]

            if len(weights) > 0:
                particle.w = max(max(weights))
            else:
                particle.w = 0

    def w_gauss2d(self, r1, r2, sigma2=500):
        return w_gauss(r1[0], r2[0], sigma2), w_gauss(r1[1], r2[1], sigma2)


if __name__ == '__main__':
    w = World()