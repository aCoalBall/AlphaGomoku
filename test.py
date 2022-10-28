from mcts import Mcts
from state import State
from net import NeuralNetwork
from train import Selfplay

import os
import torch
import numpy as np

device = 'cuda' if torch.cuda.is_available() else 'cpu'
if os.path.isfile('net_weights.pth'):
    net_model = NeuralNetwork().to(device)
    net_model.load_state_dict(torch.load('net_weights.pth'))
    net_model.eval()
else:
    net_model = NeuralNetwork().to(device)

mcts = Mcts()
state = State()

mcts.mcts_training(state, 10, net=net_model)


sp = Selfplay()
sp.set_net_models()
os.chdir(os.path.dirname(__file__))
sp.train(training_times=1, searching_times=5)
