import random
from scipy.spatial.distance import cdist
import numpy as np
import itertools
import matplotlib.pyplot as plt
import networkx as nx

class KMeansDoubleLineRemovalProcess(object):

    def __init__(self, point_cloud, lines):
        # Simulates random order of lines
        random.shuffle(point_cloud)
        self.lines = lines
        self.point_cloud = point_cloud

        before = len(point_cloud)
        point_cloud = list(set(point_cloud))
        after = len(point_cloud)

        #assert before == after
        #assert len(point_cloud)/2 == len(lines)

        line_end_points = np.array(point_cloud)
        num_lines = len(line_end_points) / 2

        Y = cdist(np.array(line_end_points), np.array(line_end_points), 'euclidean')
        plt.figure(3)
        c = plt.imshow(Y, interpolation='none')
        plt.colorbar(c)
        plt.show()

        new = np.zeros(Y.shape)

        for i in range(len(Y)):
            row = Y[i]
            h = enumerate(row)
            h = sorted(h, key=lambda x: x[1])
            idx = [e[0] for e in h[:3]]
            for idx_i in idx:
                new[i][idx_i] = 1


        self.groups = []

        plt.figure(4)
        G = nx.from_numpy_matrix(new, create_using=nx.DiGraph())
        cols = itertools.cycle(["ro", "yo", "go", "mo", "bo", "co"])
        for subg in nx.strongly_connected_component_subgraphs(G):
            v = np.array([line_end_points[e] for e in subg.nodes()])
            print "Group", v.mean(), v.std()

            self.groups.append(v)


            c = cols.next()
            for element in subg.nodes():
                a, b = line_end_points[element]
                plt.plot(a, b, c)
        plt.show()

    def get_sets_of_points(self):
        return self.groups

    def calculate_single_lines(self):
        print "########################################"

        mapping = {}

        for i in range(len(self.lines)):
            l = self.lines[i]
            mapping[str((l[0], l[1]))] = i
            mapping[str((l[2], l[3]))] = i

        IDS = []

        for group in self.groups:
            grp = [(g[0], g[1]) for g in group]
            ids = sorted([mapping[str(g)] for g in grp])
            IDS.append(ids)

        MAT = np.zeros([len(IDS), len(IDS)])

        suggested_lines = []

        for i in range(len(IDS)):
            for j in range(len(IDS)):
                if i > j:
                    if len(set(IDS[i]).__and__(set(IDS[j]))) > 0:
                        suggested_lines.append([i, j])

        print suggested_lines

        final_lines = []

        for sugl in suggested_lines:
            src_point = self.groups[sugl[0]][0]
            src_point = (src_point[0], src_point[1])
            target = mapping[str(src_point)]

            k = {k: v for k, v in mapping.items() if v == target}

            assert k.keys().__len__() == 2

            if str(src_point) == k.keys()[0]:
                target = eval(k.keys()[1])
            else:
                target = eval(k.keys()[0])

            final_lines.append([src_point[0], src_point[1], target[0], target[1]])


        plt.figure(6)
        c = plt.imshow(MAT, interpolation='none')
        plt.colorbar(c)
        plt.show()

        return final_lines
