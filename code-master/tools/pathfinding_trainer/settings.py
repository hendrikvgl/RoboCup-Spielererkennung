# -*- coding: utf-8 -*-
import time
import random
import json
#General
import itertools

p_testcases = False
p_plot = False  # Soll Beim durchlauf sachen Plotten (= Langsamer)
p_debug = False  # Soll Debugausgaben schreiben; achtung groß
p_get_last = False #Soll das Netz vom letzten Durchlauf verwenden
p_debug_folder_name = "last"  # time.strftime("%x-%X").replace("/", ".")
#                 turn, att, rep, nose, net, pops, caesse, randomcases?
p_image_folder = "images"
p_seed = time.time() # 543450# time.time()  # setzte den inituialen seed für die zufallsgeneratoren
p_seed_counter = 0  # couter, damitjedes mal ein anderer Zufall erzeugt wird
p_nr_processes = 7
p_draw_each_step = False
#getter für den seed
def p_seed_get(): global p_seed_counter; p_seed_counter += 1; return p_seed + p_seed_counter

#Network
# Number of input should be 6 in scenario with 3 objects
p_nr = [7, 5, 3]  # number of layers and neurons [input, h1, output]
# number of oput neurons should be 3


#Evolution
p_nr_itrations = 200
p_population_size = 60    # Size of the Population
p_saved_population = 3  # Number of individuals who are keept in populations and are not mutated
p_chance_mutation = 0.02  # Chance of mutatation
p_roulette_random = 0.1
#p_random_ev = lambda: ((((random.random() - 0.5)*2.5)**3)/8.0) * 20
p_random_ev = lambda: random.gauss(0, 1)
p_new_random = 0  # Number of new random nets per round
p_copy_saved = 3    # Number of copied nets from begin of list which will be mutted
p_max_weight = 5.0
p_max_bias = 6.0
p_max_tau = 4.5
p_min_tau = 0.5
p_align_manus = True
p_go_away_manus = 0.0  # Manus wenn er sich vom Ball entfernt


#Simulation
p_activated_potential_map = True
p_activated_attractors = False
p_ball_repulsor = True
p_activated_neuronal_net = True
p_potential_field_turn = False
p_nr_obstacles = 8
p_max_steps = 80 # maximum steps a robot can go
p_turn_factor = 1.1  # Factor for the turning in the simulation
p_move_factor = 10.0  # Factor for the movement
p_cases = 150
p_random_sim_cases = True  # Soll zufällige Cases verwenden
def p_input_noise(): random.seed(p_seed_get()); return random.gauss(0, 0.001)  # Zufälliger Noise der auf den Input kommt
######
#Jeden step distanz zum ball als manus addieren

if p_debug:

    with open("debug/" + p_debug_folder_name + "/general.json", "w+") as df:
        gen = [[p_get_last, p_seed],
               p_nr,
               [p_population_size, p_saved_population, p_chance_mutation,
                   p_new_random, p_copy_saved, p_go_away_manus],
               [p_max_steps, p_turn_factor, p_move_factor]]
        json.dump(gen, df)


p_cases_list = (20, 50, 90)
p_nr_list = ([7, 3, 3], [7, 5, 3], [7, 7, 3])
p_population_size_list = (30, 50, 110)
p_chance_mutation_list = (0.02, 0.05, 0.1)

it = list(itertools.product(range(3), repeat=4))
li = 0


def change():

    global p_cases, p_nr, p_population_size, p_chance_mutation, it, li
    c = it[li]
    li += 1
    p_cases = p_cases_list[c[0]]
    p_nr = p_nr_list[c[1]]
    p_population_size = p_population_size_list[c[2]]
    p_chance_mutation = p_chance_mutation_list[c[3]]
    print "p_cases ", p_cases
    print "p_nr ", p_nr
    print "p-population_size", p_population_size
    print "p_chance_mutation", p_chance_mutation
