import math
import random


def add_noise(level, *coords):
    return [x + random.uniform(-level, level) for x in coords]

def add_little_noise(*coords):
    return add_noise(0.02, *coords)

def add_some_noise(*coords):
    return add_noise(0.1, *coords)

# This is just a gaussian kernel I pulled out of my hat, to transform
# values near to robbie's measurement => 1, further away => 0
def w_gauss(a, b, sigma2=0.2**2):
    error = a - b
    g = math.e ** -(error ** 2 / (2 * sigma2))
    return g

# ------------------------------------------------------------------------
def compute_mean_point(particles, surrounding=500):
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
    m_weight = 0
    for p in particles:
        if math.sqrt((p.x - m_x)**2 + (p.y - m_y)**2) < surrounding:
            m_count += 1
            m_weight += p.w

    return m_x, m_y, m_count, m_weight



def get_uv_based_on_xy(robot_x, robot_y, orientation, target_x, target_y):
    rad_orient = (orientation / 360.0) *2 * math.pi

    x, y = robot_x, robot_y
    xb, yb = target_x, target_y

    distance = math.sqrt((x-xb)**2 + (y-yb)**2)

    delta_x = x - xb
    delta_y = y - yb

    u = -delta_x * math.cos(-rad_orient) + delta_y*math.sin(-rad_orient)
    v = delta_x * math.sin(-rad_orient) + delta_y*math.cos(-rad_orient)

    v *= -1

    return u, v

def get_uv_robot_to_robot(robot1, robot2):
    return get_uv_based_on_xy(robot1.x, robot1.y, robot1.orientation, robot2.x, robot2.y)

def get_robot_distance(robot1, robot2):
    return math.sqrt((robot1.x - robot2.x)**2 + (robot1.y - robot2.y)**2)

def add_noise_to_particle(p):
    p.x += random.gauss(0, 150)
    p.y += random.gauss(0, 150)
    p.orientation += random.gauss(0, 5)

def normalize(vector):
    value = math.sqrt(sum([v**2 for v in vector]))
    if value == 0:
        return vector
    return [v/value for v in vector]


deg2rad = 2*math.pi / 360.0

def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(L1, L2):
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x,y
    else:
        return False

def inrange(point):
    if point == False:
        return False
    return -3000.01 <= point[0] <= 3000.01 and -4500.01 <= point[1] <= 4500.01


LTOP = line([-3000,4500], [3000, 4500])
LBOTTOM = line([-3000,-4500], [3000, -4500])

LLEFT = line([-3000,-4500], [-3000, 4500])
LRIGHT = line([3000,-4500], [3000, 4500])




def get_intersect_point(x, y, omega):
    ROBOT = [x, y, omega]


    rxt = ROBOT[0] + math.cos(deg2rad*ROBOT[2]) * 300
    ryt = ROBOT[1] + math.sin(deg2rad*ROBOT[2]) * 300

    ROBOT_LINE = line([ROBOT[0], ROBOT[1]], [rxt, ryt])

    possible_points = []

    if 0 < omega < 180:
        #kann nur oben schneiden
        possible_points.append(intersection(LTOP, ROBOT_LINE))
    elif 180 < omega < 360:
        # kann nur unten schneiden
        possible_points.append(intersection(LBOTTOM, ROBOT_LINE))
    elif omega == 0 or omega == 180 or omega == 360:
        # schneided weder unten noch oben
        pass
    else:
        # groesser als 360
        pass

    if 0 <= omega < 90:
        #kann nur rechts schneiden
        possible_points.append(intersection(LRIGHT, ROBOT_LINE))
    elif 90 < omega < 270:
        # kann nur links schneiden
        possible_points.append(intersection(LLEFT, ROBOT_LINE))
    elif 270 < omega <= 360:
        # kann nur rechts schneiden
        possible_points.append(intersection(LRIGHT, ROBOT_LINE))
    elif omega == 90 or omega == 270 or omega == 360:
        pass
        # schneided weder unten noch oben
    else:
        pass
        # groesser als 360

    possible_points = [p for p in possible_points if inrange(p)]

    if len(possible_points) == 0:
        return (10000000,1000000)
    try:
        assert len(possible_points) == 1, ROBOT
    except:
        assert len(possible_points) == 2, ("Not exatctly 2 points", ROBOT)
        a, b = possible_points
        dst = math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
        if dst < 1E-2:
            del possible_points[0]
        else:
            assert False, (ROBOT, dst)



    return possible_points[0]


def get_particle_intersect_point(particle, angle_offset=0):
    return get_intersect_point(particle.x, particle.y, (particle.orientation+angle_offset) % 360)
