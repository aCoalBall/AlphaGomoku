import copy
import os
import torch
import numpy as np
from torch import nn
from mcts import Mcts
from state import State
from net import NeuralNetwork
from global_var import BOARD_SIZE, ONGOING, BLACK, WHITE, DRAW, UNCHECKED

class Selfplay :
    def __init__(self):
        self.explorer = Mcts()
        self.net = None
        self.learning_rate = 1e-2
        self.loss_func = nn.MSELoss()
        self.optimizer = None
        self.device = ''

    def set_net_models(self, learning_rate = None, loss_func = None):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.net = NeuralNetwork().to(self.device)
        if os.path.isfile('net_weights.pth'):
            self.net.load_state_dict(torch.load('net_weights.pth'))
            self.net.eval()
        if learning_rate != None:
            self.learning_rate = learning_rate
        if loss_func != None:
            self.loss_func = loss_func
        self.optimizer = torch.optim.SGD(self.net.parameters(), lr = self.learning_rate)
    
    def train(self, training_times, searching_times):
        for i in range(training_times) :
            self.explorer = Mcts()
            res, states, moves, player = self.play_one_game(searching_times)
            batch = self.get_net_input(states, moves, player)
            standard = self.get_net_standard(res, states)
            self.optimize(batch, standard)
            print(i+1, 'rounds done')
        self.save_net('net_weights.pth')

    def test(self, searching_times) :
        sum_loss = 0
        self.explorer = Mcts()
        res, states, moves, player = self.play_one_game(searching_times)
        batch = self.get_net_input(states, moves, player)
        standard = self.get_net_standard(res, states)
        pred_value = self.net(batch)
        loss = self.loss_func(pred_value, standard)
        sum_loss += loss.item()
        return sum_loss


    def play_one_game(self, searching_times):
        #reset
        self.explorer = Mcts()
        game = State()
        game_history = []
        move_history = []

        while game.check_game_result() == ONGOING :
            game_history.append(copy.deepcopy(game))
            self.explorer.mcts_training(state = game, times = searching_times, net = self.net)
            move , game = self.explorer.best_choice_from_root_node()
            move_history.append(move)
        
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
        if result == DRAW :
            result = 0
        elif result == BLACK:
            result = 1
        elif result == WHITE:
            result = -1
        results = []
        for state in game_history : 
            results.append(result)
        results = torch.tensor(results, dtype=torch.float)
        if self.device == 'cuda':
            results = results.cuda()
        return results
                
    def get_net_input(self, game_history, move_history, player):
        batch_size = len(game_history)
        game_history = [State(), State(),] + game_history
        batch = []
        for i in range(batch_size) :
            state1 = game_history[i].chessboard
            state2 = game_history[i+1].chessboard

            if player[i] == 1 :
                player_state = [[1 for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]
            elif player[i] == 2 :
                player_state = [[2 for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]

            move_state = [[0 for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]
            x,y = move_history[i]
            move_state[x][y] = player[i]

            sample = [state1, state2, player_state, move_state]
            batch.append(sample)

        batch = torch.tensor(batch, dtype=torch.float)
        if self.device == 'cuda':
            batch = batch.cuda()
        return batch
    
    def optimize(self, batch, standard) :
        pred_value = self.net(batch)
        loss = self.loss_func(pred_value, standard) 

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def save_net(self, filename) :
        torch.save(self.net.state_dict(), filename)

