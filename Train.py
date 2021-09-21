import random
import copy
import math
import os
import numpy
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import torchvision.models as models

from gomoku import *
from MonteCarloTS import MonteCarlo
from BoardForMCTS import Board
from GomokuNet import NeuralNetwork
from GomokuNet import NET
    


class Selfplay :
    def __init__(self):
        self.explorer = MonteCarlo()
        self.learning_rate = 1e-3
        self.loss_mse = nn.MSELoss()
        self.optimizer = torch.optim.SGD(NET.parameters(), lr = self.learning_rate)

    def play_one_game(self, searching_times):
        #reset
        game = Board()
        game_history = []
        move_history = []

        while game.check_game_result() == 0 :
            game_history.append(copy.deepcopy(game))
            self.explorer.mcts_training(game, searching_times)
            game , move = self.explorer.best_choice(game)
            move_history.append(move)
            print(move)
        
        player = []
        for i in range(len(move_history)) :
            if (i + 1) % 2 == 1 :
                player.append(BLACK)
            else :
                player.append(WHITE)

        return (game.check_game_result(),
            game_history, 
            move_history,
            player)
    
    def get_net_standard(self, result, game_history) :
        if result == 3 :
            result = 1.5
        result = [result]

        results = []


        for state in game_history : 
            results.append(result)


        results = torch.tensor(results, dtype=torch.float)
        return results
                

    
    def get_net_input(self, game_history, move_history, player):

        batch_size = len(game_history)
        game_history = [Board(), Board(), Board()] + game_history


        batch = []
        for i in range(batch_size) :
            state1 = game_history[i].game_map
            state2 = game_history[i+1].game_map
            state3 = game_history[i+2].game_map
            state4 = game_history[i+3].game_map

            if player[i] == 1 :
                player_state = [[1 for y in range(15)] for x in range(15)]
            elif player[i] == 2 :
                player_state = [[2 for y in range(15)] for x in range(15)]

            move_state = [[0 for y in range(15)] for x in range(15)]
            x,y = move_history[i]
            move_state[x][y] = player[i]

            sample = [state1, state2, state3, state4, player_state, move_state]
            batch.append(sample)

        batch = torch.tensor(batch, dtype=torch.float)
        return batch
        

    def optimize(self, batch, standard) :
        pred_value = NET(batch)
        loss = self.loss_mse(pred_value, standard) 

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


    def save_net(self, filename) :
        torch.save(NET.state_dict(), filename)




def train(training_times, searching_times) :
    sp = Selfplay()
    for i in range(training_times) :
        res, states, moves, player = sp.play_one_game(searching_times)
        print(res)
        print(len(moves))
        print(len(player))

        batch = sp.get_net_input(states, moves, player)
        standard = sp.get_net_standard(res, states)
        sp.optimize(batch, standard)

        print(i+1, 'rounds done')

    sp.save_net('net_weights.pth')



def test(searching_times) :
    sp_test = Selfplay()
    sum_loss = 0
    for i in range(2) :
        res, states, moves, player = sp_test.play_one_game(searching_times)
        batch = sp_test.get_net_input(states, moves, player)
        standard = sp_test.get_net_standard(res, states)
        pred_value = NET(batch)
        loss_mse = nn.MSELoss()
        loss = loss_mse(pred_value, standard)
        sum_loss += loss.item()
    
    sum_loss = sum_loss / 2.0
    print(sum_loss)
    return sum_loss



def main() :

    
    os.chdir(os.path.dirname(__file__))
    train(training_times=2000, searching_times=1)
    loss_trend = []
    for i in range(100) :
        train(training_times=30, searching_times=100)
        loss = test(searching_times=100)
        loss_trend.append(loss)
        numpy.save('current_loop.npy', i)
    numpy.save('loss_trend_list.npy', loss_trend)
  
    
    
if __name__ == '__main__' :
    main()