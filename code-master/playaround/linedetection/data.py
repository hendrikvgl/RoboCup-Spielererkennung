import random
import numpy as np

def giveit():
    m = [
        (10, 10),
        (150, 10),
        (100, 10),
        (100, 50),
        (250, 50)
    ]

    step_division = 500
    noise = 2
    points = []

    for i in range(len(m) -1):
        a, b = m[i], m[i+1]

        for k in range(step_division):
            p = k / float(step_division)

            px = a[0]*p + (1-p)*b[0]
            py = a[1]*p + (1-p)*b[1]

            px = random.gauss(px, noise)
            py = random.gauss(py, noise)

            points.append([px, py])

    maxx = max([e[0] for e in points])
    maxy = max([e[1] for e in points])

    maxx = int(maxx)
    maxy = int(maxy) + 10

    IMG = np.zeros((maxy, maxx),  dtype=np.uint8)

    for element in points:
        try:
            y, x = element
            x, y = int(x), int(y)
            IMG[x][y] = 255
        except:
            pass
    return IMG, points
