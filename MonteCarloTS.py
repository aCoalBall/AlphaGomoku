import random
import copy
import math
import os
import torch
import numpy

import GomokuNet
from gomoku import *
from BoardForMCTS import Board
from GomokuNet import NeuralNetwork
from GomokuNet import NET

BLACK = 1
WHITE = 2
STATUS = 0
WINNING_RATE = 1
ALL_MOVES = 2


class MonteCarlo :

    def __init__(self) :
        self.current_state = Board()
        self.current_move = None
        #total exploration times
        self.total_attempts = 1
        #for each state, record its status, and its winning rate 
        # in the form (status, [win, all])
        self.states_dic = {}
        #add the root state to the dictionary
        cp = Board()
        self.states_dic[cp] = (0, [0, 0])
        #the trace of our exploration
        self.history = []

    def mcts_training(self, given_state, times) :
        for i in range(times) :
            self.selection(given_state)
            self.expansion()
            result = self.simulation()
            self.back_propagation(result)
            self.total_attempts += 1

    def best_choice(self, given_state) :
        if given_state.check_game_result() != 0 :
            return None
        legal_moves = given_state.possible_choices()
        legal_states_dic = {}

        for move in legal_moves :
            cp = copy.deepcopy(given_state)
            cp.play(move[0], move[1])
            legal_states_dic[cp] = move
        
        childs = legal_states_dic.keys()
        if len(childs):
            best_child =  copy.deepcopy(self.ucb1(legal_states_dic))
        else :
            return None

        return (best_child, legal_states_dic[best_child])

    def possible_states(self, given_state) :
        #set of legal moves
        legal_moves = given_state.possible_choices()
        #init set of legal states by taking legal moves
        legal_states = set()
        for move in legal_moves :
            cp = copy.deepcopy(given_state)
            cp.play(move[0], move[1])
            legal_states.add(cp)
        return legal_states


    def selection(self, given_state) :
        #new begining, init the current state and its parent to the root
        self.current_state = copy.deepcopy(given_state)

        #add given state to the dictionary(tree)
        if self.current_state not in self.states_dic :
            res = self.current_state.check_game_result()
            if res == 0 :
                self.states_dic[copy.deepcopy(given_state)] = (res, [0, 0])
            else :
                self.states_dic[copy.deepcopy(given_state)] = (res, None)

        #clear the trace
        self.history = []
        
        #explore the tree until reaching ends or meeting a new node
        while (self.current_state in self.states_dic) and (self.current_state.check_game_result() == 0):
            #choose the "best" choice given by ucb1
            #track the path of exploration
            self.history.append(copy.deepcopy(self.current_state))
            temp = self.best_choice(self.current_state)
            if temp != None :
                best_state, best_move = temp
            else :
                break

            self.current_state = copy.deepcopy(best_state)
            self.current_move = best_move
        
        #reached an unexplored state, selection is over, now time to expansion


    def expansion(self) :
        #add the new node to the trace
        cp = copy.deepcopy(self.current_state)
        self.history.append(copy.deepcopy(self.current_state))

        #add the new node to the dictionary
        res = cp.check_game_result()
        if res != 0 :
            self.states_dic[cp] = (res, None)
        else :
            if cp not in self.states_dic :
                self.states_dic[cp] = (0, [0, 0])

    
    def simulation(self) :
        res = self.current_state.check_game_result()
        if res == 0 :
            value = self.forward_net()
        
            value = value.item()
            if value < 1.5 :
                return 1
            elif value == 1.5 :
                return 3
            elif value > 1.5 :
                return 2
            else :
                return "wrong"
        else :
            return res


    def back_propagation(self, result) :
        for state in self.history :
            if self.states_dic[state][STATUS] == 0 :
                self.states_dic[state][WINNING_RATE][1] += 1
        #if black wins    
        if result == 1 :
            for state in self.history :
                if self.states_dic[state][STATUS] == 0 and state.player == BLACK :
                    self.states_dic[state][WINNING_RATE][0] += 1
        #if white wins
        elif result == 2 :
            for state in self.history :
                if self.states_dic[state][STATUS] == 0 and state.player == WHITE :
                    self.states_dic[state][WINNING_RATE][0] += 1
        #else, nothing to do

    
    def forward_net(self) :
        simulate_state = copy.deepcopy(self.current_state)
        copy_history = copy.deepcopy(self.history)

        while len(copy_history) < 4 :
            copy_history = [Board(),] + copy_history

        previous = copy_history[-4:]
        state1 = previous[0].game_map
        state2 = previous[1].game_map
        state3 = previous[2].game_map
        state4 = previous[3].game_map

        if simulate_state.player == 1 :
            player_state = [[1 for y in range(15)] for x in range(15)]
        elif simulate_state.player == 2 :
            player_state = [[2 for y in range(15)] for x in range(15)]

        move_state = [[0 for y in range(15)] for x in range(15)]
        x,y = self.current_move
        move_state[x][y] = simulate_state.player

        sample = [state1, state2, state3, state4, player_state, move_state]
        batch = [sample]
        batch = torch.tensor(batch, dtype=torch.float)
        value = NET(batch)

        return value 


    def ucb1(self, child_states_dic) :
        max_ucb = -1000
        chosen = None

        for state in child_states_dic :
            res = state.check_game_result()
            x, y = child_states_dic[state]
            #if reached an end state
            if res != 0 :
                if res == 3 :
                    upper_bound = 0.55
                elif res == 2 :
                    if state.player == WHITE :
                        upper_bound = -100
                    elif state.player == BLACK :
                        upper_bound = 100
                elif res == 1 :
                    if state.player == WHITE :
                        upper_bound = 100
                    elif state.player == BLACK :
                        upper_bound = -100
            #if reached a state not in dictionary
            elif state not in self.states_dic :
                attempts = 0
                mean = 0.5
                upper_bound = mean + math.sqrt(2 * math.log(self.total_attempts) / float(1 + attempts)) + random.random() / 12.0
            else :
                attempts = self.states_dic[state][WINNING_RATE][1]
                wins = self.states_dic[state][WINNING_RATE][0]
                if attempts != 0:
                    mean = 1 - float((wins / attempts))
                else :
                    mean = 0.5
                upper_bound = mean + math.sqrt(2 * math.log(self.total_attempts) / float(1 + attempts)) + random.random() / 12.0

            if upper_bound >= max_ucb :
                max_ucb = upper_bound
                chosen = state
        '''
        if chosen in self.states_dic :
            print(self.states_dic[chosen][WINNING_RATE][1])
        else :
            print(0)
        '''
        
        
        return chosen






