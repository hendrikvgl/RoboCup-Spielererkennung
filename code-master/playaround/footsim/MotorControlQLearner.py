# -*- coding:utf-8 -*-
from itertools import combinations, product
import random

ACTIONS = list(product([-5, 0, 5], [-5, 0, 5], [-5, 0, 5], [-5, 0, 5]))

class RobotFootQLearner():

    def __init__(self, inital_state):
        self.agent_state = inital_state
        # The Q-Learning Structure
        self.init_Q()

    def init_Q(self):
        self.Q = {}

        # States is the distance to the
        for cPressureA in range(0, 20):
            self.Q[cPressureA] = {}
            for cPressureB in range(0, 20):
                self.Q[cPressureA][cPressureB] = {}
                for cPressureC in range(0, 20):
                    self.Q[cPressureA][cPressureB][cPressureC] = {}
                    for action in ACTIONS:
                        self.Q[cPressureA][cPressureB][cPressureC][str(action)] = random.random()


    def helper_maximum(self, nextstate):
        cPressureA, cPressureB, cPressureC = nextstate
        return max(list(self.Q[cPressureA][cPressureB][cPressureC].values()))

    def reset_reward(self):
        self.accumulated_reward = 0

    def helper_max_next_action(self):
        cPressureA, cPressureB, cPressureC = self.agent_state
        dic = self.Q[cPressureA][cPressureB][cPressureC]
        v = list(dic.values())
        k = list(dic.keys())
        return k[v.index(max(v))]

    def helper_max_next_action_outside(self, dic):
        v = list(dic.values())
        k = list(dic.keys())
        return k[v.index(max(v))]

    def perform_q_learning(self, current, action, reward, nextstate, alpha=0.2, gamma=0.9):
        #print "Learning with: %s -> %s with reward %i and action %s" % (str(current), str(nextstate), reward, action)
        cPressureA, cPressureB, cPressureC = current
        self.Q[cPressureA][cPressureB][cPressureC][action] = (1 - alpha)*self.Q[cPressureA][cPressureB][cPressureC][action] + alpha * (reward + gamma * self.helper_maximum(nextstate))

    def decide_next_action(self, learning):
        if learning:
            action = ACTIONS[int(len(ACTIONS)*random.random())]
            if random.random() > 0.2:
                action = self.helper_max_next_action()
            return action
        else:
            action = self.helper_max_next_action()
            if random.random() > 0.95:
                action = ACTIONS[int(len(ACTIONS)*random.random())]
            return action

    def perform(self, learning, current_state, afteraction_state, reward):
        # Determine the next action
        nextaction = self.decide_next_action(learning)

        if learning:
            self.perform_q_learning(current_state, nextaction, reward, afteraction_state)

        return nextaction

    def update_state(self, state):
        self.agent_state = state