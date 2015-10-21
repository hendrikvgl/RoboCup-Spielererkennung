from simulator import Simulator
from evolution import Evolutor
import os
import cPickle as pickle
from settings import *
if __name__ == '__main__':
    simulator = Simulator()

    ev = Evolutor()
    x = len(li) if p_testcases else 1
    try:
        for o in range(x):
            if p_testcases:
                change()

            for i in range(p_nr_itrations):
                last = i == (p_nr_itrations - 1)
                ev.step(last)
                simulator.simulate(ev.actuall_best_net, i % 20 == 0)
                if i == 119 or not p_testcases:
                    print "Generation: ", i, " Best: ", ev.actuall_best_net_val/float(p_cases), " Total: ", ev.actuall_population_performance

    finally:
        f = file("network.pickle", "wb")

        #for w in ev.population[0].weights.values():
        #    print w
        #print "bias: \n"
        #for l in ev.population[0].layers:
        #    for n in l:
        #        print n.b
        pickle.dump(ev.actuall_best_net, f, 0)
        f.close()

        writer = file("top_net.dt", "w")
        writer.write("digraph Network {\nrankdir=LR;\n")
        for l in ev.population[0].layers:
            n = 0
            for neuron in l:
                writer.write(str(neuron) + " [label=\"" + str(n) + " - " + str("N") + " - " + "{:2.4f}".format(
                    neuron.b) + "\", shape=ellipse];\n")
                n += 1
        weights = ev.population[0].weights
        for f, t in weights:
            writer.write(str(f) + "->" + str(t) + "[label=\"" + "{:2.4f}".format(weights[(f, t)]) + "\"];\n")
        writer.write("}")
        writer.close()
        os.system("dot top_net.dt -Tpng -o net.png")

