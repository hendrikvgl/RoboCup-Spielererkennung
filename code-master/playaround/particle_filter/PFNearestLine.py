import math
from Particle import FeaturedParticle

__author__ = 'sheepy'

class PFNearest(object):

    def __init__(self, field, robot):
        self.field_points = field

        self.robot = robot

        self.particles = []
        for i in range(-3000, 3000, 200):
            for j in range(-4500, 4500, 200):
                self.particles.append(FeaturedParticle(i, j, 0))

    def algorithm_run(self):
        # Calculate what the robot is sensing with noise
        self.calculate_angles_for_defined_particle(self.robot)

        self.robot.features = {k: v for k, v in self.robot.features.items()}

        # Calculate what the particles are sensing
        for p in self.particles:
            self.calculate_angles_for_defined_particle(p)

        # Calculate the Similarity between Particles and Robots Sensing and assign weight based on that
        self.calculate_similarity_and_assign_weight()

        # Normalize the Weight of the Particles
        self.normalize_particles(self.particles)

        # Generate new Particles based on the Weighted Distribution
        # self.particles = self.make_new_particle_cloud(self.particles)

    def normalize_particles(self, particles):
        # Normalise weights
        nu = sum(p.w for p in particles)
        if nu:
            for p in particles:
                p.w = p.w / nu

    def calculate_similarity_and_assign_weight(self):
        dp_r1 = [self.robot.features[i] for i in range(0, 3, 1)]

        for particle in self.particles:
            dp_p = [particle.features[i] for i in range(0, 3, 1)]

            a1 = abs(dp_p[0] - dp_r1[0])
            b1 = abs(dp_p[1] - dp_r1[1])
            c1 = abs(dp_p[2] - dp_r1[2])

            kmn = (a1 + b1 + c1)**0.3
            if kmn == 0:
                h1 = 999
            else:
                h1 = 1 / kmn

            particle.w = h1
            continue

    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2+(p1[1] - p2[1])**2)

    def calculate_angles_for_defined_particle(self, particle):
        distances = [self.distance(fp, (particle.x, particle.y)) for fp in self.field_points]
        mindst = min(distances)
        maxdst = max(distances)
        particle.add_feature(0, mindst)
        particle.add_feature(1, maxdst)
        particle.add_feature(2, self.distance((0, 0), (particle.x, particle.y)))

    def make_new_particle_cloud(self, particles):
        """ wd = WeightedDistribution(particles)
        newparticles = []
        while len(newparticles) < PARTICLE_COUNT:
            picked = wd.pick()
            if picked is None:
                picked = FeaturedParticle(random.randint(-3000, 3000), random.randint(-4500, 4500), random.randint(0, 360))
            else:
                #picked = FeaturedParticle(random.randint(-3000, 3000), random.randint(-4500, 4500), random.randint(0, 360))
                picked = FeaturedParticle(picked.x, picked.y, picked.orientation)
            add_noise_to_particle(picked)
            newparticles.append(picked)"""
        return particles


