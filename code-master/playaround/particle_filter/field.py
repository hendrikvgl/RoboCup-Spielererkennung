# -*- coding:utf-8 -*-
import random
import math


def get_field():
    G = 200

    X = [(random.randint(-25, 25), random.randint(-3000, 3000)) for e in range(G)]
    X += [(random.randint(-25, 25), random.randint(-3000, 3000)) for e in range(G)]

    X += [(random.randint(-4500-25, -4500+25), random.randint(-3000, 3000)) for e in range(G)]
    X += [(random.randint(4500-25, 4500+25), random.randint(-3000, 3000)) for e in range(G)]

    X += [(random.randint(-4500, 4500), random.randint(-3000-25, -3000+25)) for e in range(G)]
    X += [(random.randint(-4500, 4500), random.randint(3000-25, 3000+25)) for e in range(G)]

    klist = [random.random() for jk in range(G*3)]
    X += [(1500*math.cos(k*2*math.pi), 1500*math.sin(k*2*math.pi)) for k in klist]

    X = [(x[1], x[0]) for x in X]

    return X