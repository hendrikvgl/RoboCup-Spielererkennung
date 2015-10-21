# -*- coding: utf-8 -*-
import copy
import itertools
import cPickle as Pickle

from network import Network
from simulator import Simulator
from settings import *
import network
from multiprocessing import Pool





class Evolutor(object):

    def __init__(self):
        """
        Creates the population, by random values or bases of earlier run
        :return: None
        """
        self.population = []
        self.survivors = []
        self.actuall_population_performance = 0
        self.actuall_best_net_val = 0
        self.actuall_best_net = 0
        self.simulator = Simulator()
        self.pool = Pool(p_nr_processes)

        try:
            if not p_get_last:
                raise ValueError
            f = file("network.pickle", "rb")
            netw = Pickle.load(f)

            #for i in xrange(p_population_size/2):
            #    self.population.append(self.create_random_network())

            for i in xrange(p_population_size):
                self.population.append(copy.deepcopy(netw))
            f.close()

        except (IOError, ValueError):

            for i in xrange(p_population_size):
                self.population.append(self.create_random_network())

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    @staticmethod
    def create_random_network():
        """
        Creates a new Network with random Values
        :return: the createted Network
        :rtype Network
        """
        net = Network()

        #initialiaze weights
        for l in range(len(p_nr)-1):
            for x, y in itertools.product(net.layers[l], net.layers[l+1]):
                random.seed(p_seed_get())
                net.weights[(x, y)] = p_random_ev()
        # fully connected hidden layer
        for l in range(1, len(net.layers) - 1):
            for x, y in itertools.product(net.layers[1], net.layers[1]):
                random.seed(p_seed_get())
                net.weights[(x, y)] = p_random_ev()

        return net

    def rate(self):
        """
        Rates the fittnes of a network with the Simulator
        :return: Ranked list of tuples with fittnes an the network
        :rtype: list
        """
        ranked_list = []
        f_list = []

        qn = self.pool.map(self.simulator.simulate, self.population)
        for qual, net in qn:
            f_list.append(qual)
            ranked_list.append((qual, net))
        if self.simulator.PLOT:
            self.simulator.gui.plot_fitness(f_list)

        return ranked_list

    @staticmethod
    def rank(ranked_list):
        """
        Sorts the given list by fittness
        :param ranked_list: List of tuples of Fitnnes and Network
        :type ranked_list: list
        :return: sorted list, first element ist fittest
        :rtype: list
        """
        return sorted(ranked_list, key=lambda x: x[0])

    def reduce(self, ranked_list):
        """
        Gets the ranked list and createts smaller  new Population out of it
        :param ranked_list: already sorted list of tuples with fittnes and Networks
        :type ranked_list: list
        :return: None
        """
        self.population = [x[1] for x in ranked_list[:-(p_new_random+p_copy_saved)]]

    def mutate(self):
        """
        Mutates the current population.
        Weights are changed by random 8and parametes
        :return: None
        """
        for net in self.population:
            for l in range(len(net.layers)-1):

                #mutate weights
                for x, y in itertools.product(net.layers[l], net.layers[l+1]):
                    random.seed(p_seed_get())
                    if random.random() <= p_chance_mutation:
                        #mutate
                        random.seed(p_seed_get())
                        rand_w = p_random_ev()
                        if rand_w > 0 and net.weights[(x, y)] + rand_w > p_max_weight:
                            net.weights[(x, y)] = p_max_weight - rand_w

                        elif rand_w < 0 and net.weights[(x, y)] + rand_w < -p_max_weight:
                            net.weights[(x, y)] = -p_max_weight - rand_w

                        else:
                            net.weights[(x, y)] += rand_w
                            #mutate weights

            for x, y in itertools.product(net.layers[1], net.layers[1]):
                random.seed(p_seed_get())
                if random.random() <= p_chance_mutation:
                    #mutate
                    random.seed(p_seed_get())
                    rand_w = p_random_ev()

                    if rand_w > 0 and net.weights[(x, y)] + rand_w > p_max_weight:
                        net.weights[(x, y)] = p_max_weight - rand_w

                    elif rand_w < 0 and net.weights[(x, y)] + rand_w < -p_max_weight:
                        net.weights[(x, y)] = -p_max_weight - rand_w

                    else:
                        net.weights[(x, y)] += rand_w
            #mutate bias
            for l in range(len(net.layers)):
                for n in net.layers[l]:
                    random.seed(p_seed_get())
                    if random.random() <= p_chance_mutation:
                        random.seed(p_seed_get())
                        rand_b = p_random_ev() / 10.0
                        if rand_b > 0 and n.b + rand_b > p_max_bias:
                            n.b = p_max_bias - rand_b

                        elif rand_b < 0 and n.b + rand_b < -p_max_bias:
                            n.b = -p_max_bias - rand_b

                        else:
                            n.b += rand_b
            #mutate tau
            for l in range(len(net.layers)):
                for n in net.layers[l]:
                    random.seed(p_seed_get())
                    if random.random() <= p_chance_mutation:
                        random.seed(p_seed_get())
                        rand_t = p_random_ev()

                        if rand_t > 0 and n.tau + rand_t > p_max_tau:
                            n.tau = p_max_tau - rand_t
                        elif rand_t < 0 and n.tau + rand_t < p_min_tau:
                            n.tau = p_min_tau - rand_t
                        else:
                            n.tau += rand_t

            net.version += 1  # Version of the net +1

    def selection(self, sorted_list):
        """
        Selects the childs for the next genereration
        :return: None
        """
        # clear list of survivors and old population
        self.survivors = []
        self.population = []

        # creates new random networks
        for i in xrange(p_new_random):
            self.population.append(self.create_random_network())

        # saves survivors
        for i in xrange(p_copy_saved):
            cnet = self.copy(sorted_list[i][1])

            self.survivors.append(cnet)

        # Gets fittnes of population

        fittnes_list = map(lambda x: x[0], sorted_list)
        cum_fittnes = sum(fittnes_list)

        #statistics

        self.actuall_population_performance = cum_fittnes
        self.actuall_best_net_val = sorted_list[0][0]
        self.actuall_best_net = copy.deepcopy(sorted_list[0][1])

        # add more childs if population is not complete
        while len(self.population) + p_copy_saved < p_population_size:
            """
            # Generates random treshhold when net is selected
            random.seed(p_seed_get())
            treshhold = random.random() * cum_fittnes

            cum_rate = 0
            for rate, net in sorted_list:
                cum_rate += rate
                if cum_rate >= treshhold:
                    self.population.append(self.copy(net))
                    break
            """
            for rate, net in sorted_list:
                random.seed(p_seed_get())
                if random.random() < p_roulette_random:
                    self.population.append(self.copy(net))
                    break

    @staticmethod
    def copy(onet):
        """
        Deepcopys network
        :param onet:
        :return:
        """
        cnet = copy.deepcopy(onet)
        cnet.id = network.ncounter
        network.ncounter += 1
        cnet.parent = (onet.id, onet.version)
        cnet.version = 0
        return cnet

    def add_survivors(self):
        """
        Adds the selectet survivors again to the population
        :return: None
        """
        self.population.extend(self.survivors)

    def step(self, last):
        """
        Produces one step/ one Generation in the evlolution
        :return: None
        :param last: letzte runde?
        """

        # Rates the actuall population and gives a sorted list of tuples with fittnes and the network
        sorted_list = self.rank(self.rate())

        # Selects the Children and Survivors for the new generation
        self.selection(sorted_list)

        if not last:# in last round dont mutate
            # Mutates the new childs

            self.mutate()

        # Adds the survivors of the last round
        self.add_survivors()

        #self.reduce(sorted_list)

        if p_debug:
            with open("debug/"+p_debug_folder_name+"/networks.json", "a") as js:
                for net in self.population:
                    netinf = [net.id, net.parent, net.version]
                    for i in net.weights.values():
                        netinf.append(i)
                    json.dump(netinf, js)
                    js.write("\n")
