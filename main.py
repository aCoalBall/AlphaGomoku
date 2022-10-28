from gomoku import *
from train import Selfplay

from PyQt5.QtWidgets import *
import sys
from GUI import *
import os

def game_mode() :
    '''game mode, when call this func, the user can play with ai'''
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
    app = QApplication(sys.argv)
    ex = GomokuWindow()
    sys.exit(app.exec_())

def train_mode(training_times = 50) :
    '''train mode, when call this func, the user can train the ai'''
    os.chdir(os.path.dirname(__file__))
    sp = Selfplay()
    sp.set_net_models()
    loss_trend = []
    for i in range(1) :
        sp.train(training_times, searching_times=200)
        loss = sp.test(searching_times=200)
        loss_trend.append(loss)
        np.save('current_loop.npy', i)
    np.save('loss_trend_list.npy', loss_trend)

def main():
    '''the main func, the start point'''
    if len(sys.argv) == 1:
        game_mode()
    elif len(sys.argv) == 2:
        mode = sys.argv[1]
        if mode == 'play':
            game_mode()
        elif mode == 'train':
            train_mode()
        else:
            print('please enter mode type: train or play')
    elif len(sys.argv) == 3:
        if mode == 'train':
            train_mode(int(sys.argv[2]))

    else:
        print('invalid command')

if __name__ == '__main__' :
    main()