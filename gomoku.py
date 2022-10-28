from state import State
from mcts import *
from net import NeuralNetwork
from global_var import BOARD_SIZE, ONGOING, BLACK, WHITE, DRAW, UNCHECKED

import os


class Game(State) :
    '''
    The game for user playing with AI, different with State class, Game is connencted to user interface
    '''
    def __init__(self) :
        """constructor"""
        super().__init__()
        self.number_of_steps = 0 #Count total steps
        #Load the net
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        if os.path.isfile('net_weights.pth'):
            self.net = NeuralNetwork().to(device)
            self.net.load_state_dict(torch.load('net_weights.pth'))
            self.net.eval()
        else:
            self.net = NeuralNetwork().to(device)
    
    def check_game_result(self, show = False) :
        """return 0 if the game keeps going
           return 1 if the BLACK wins
           return 2 if the WHITE wins
           return 3 if it's a draw"""
        #1 check horizontal direction
        for x in range(BOARD_SIZE - 4) :
            for y in range(BOARD_SIZE - 4) :
                if self.chessboard[x+4][y] == 1 and self.chessboard[x+3][y] == 1 and self.chessboard[x+2][y] == 1 and self.chessboard[x+1][y] == 1 and self.chessboard[x][y] == 1 :
                    if show:
                        return BLACK, [(x0, y) for x0 in range(x, x + 5)]
                    else:
                        return BLACK
                if self.chessboard[x+4][y] == 2 and self.chessboard[x+3][y] == 2 and self.chessboard[x+2][y] == 2 and self.chessboard[x+1][y] == 2 and self.chessboard[x][y] == 2 :
                    if show:
                        return WHITE, [(x0, y) for x0 in range(x, x + 5)]
                    else:
                        return WHITE

        #2 check vertical direction
        for x in range(BOARD_SIZE - 4) :
            for y in range(BOARD_SIZE - 4) :
                if self.chessboard[x][y] == 1 and self.chessboard[x][y+1] == 1 and self.chessboard[x][y+2] == 1 and self.chessboard[x][y+3] == 1 and self.chessboard[x][y+4] == 1 :
                    if show:
                        return BLACK, [(x, y0) for y0 in range(y, y + 5)]
                    else:
                        return BLACK
                if self.chessboard[x][y] == 2 and self.chessboard[x][y+1] == 2 and self.chessboard[x][y+2] == 2 and self.chessboard[x][y+3] == 2 and self.chessboard[x][y+4] == 2 :
                    if show:
                        return WHITE, [(x, y0) for y0 in range(y, y + 5)]
                    else:
                        return WHITE

        #3 check from upper-left to lower-right
        for x in range(BOARD_SIZE - 4) :
            for y in range(BOARD_SIZE - 4) :
                if self.chessboard[x][y+4] == 1 and self.chessboard[x+1][y+3] == 1 and self.chessboard[x+2][y+2] == 1 and self.chessboard[x+3][y+1] == 1 and self.chessboard[x+4][y] == 1 :
                    if show:
                        return BLACK, [(x + t, y + 4 - t) for t in range(5)]
                    else:
                        return BLACK
                if self.chessboard[x][y+4] == 2 and self.chessboard[x+1][y+3] == 2 and self.chessboard[x+2][y+2] == 2 and self.chessboard[x+3][y+1] == 2 and self.chessboard[x+4][y] == 2 :
                    if show:
                        return WHITE, [(x + t, y + 4 - t) for t in range(5)]
                    else:
                        return WHITE

        #4 check from upper-right to lower-left
        for x in range(BOARD_SIZE - 4) :
            for y in range(BOARD_SIZE - 4) :
                if self.chessboard[x+4][y+4] == 1 and self.chessboard[x+3][y+3] == 1 and self.chessboard[x+2][y+2] == 1 and self.chessboard[x+1][y+1] == 1 and self.chessboard[x][y] == 1 :
                    if show:
                        return BLACK, [(x + t, y + t) for t in range(5)]
                    else:
                        return BLACK
                if self.chessboard[x+4][y+4] == 2 and self.chessboard[x+3][y+3] == 2 and self.chessboard[x+2][y+2] == 2 and self.chessboard[x+1][y+1] == 2 and self.chessboard[x][y] == 2 :
                    if show:
                        return WHITE, [(x + t, y + t) for t in range(5)]
                    else:
                        return WHITE
        #5 check if it's a draw
        for x in range(BOARD_SIZE) :
            for y in range(BOARD_SIZE) :
                if self.chessboard[x][y] == 0 :
                    return ONGOING, [(-1, -1)]

        return DRAW, [(-1, -1)]

    
    def player_move(self, input_by_window=False, pos_x=None, pos_y=None) :
        """player's step"""
        while True :
            try :
                if not input_by_window:
                    pos_x = int(input('x: '))  #player's input
                    pos_y = int(input('y: '))
                if 0 <= pos_x <= (BOARD_SIZE - 1) and 0 <= pos_y <= (BOARD_SIZE - 1) :
                    if self.chessboard[pos_x][pos_y] == 0:
                        self.chessboard[pos_x][pos_y] = 1
                        self.player = WHITE
                        self.number_of_steps += 1
                        return
            except ValueError :
                continue
    

    def ai_move(self) :
        """AI's step"""
        current_state = State(chessboard = self.chessboard, player = self.player)
        mc = Mcts() #use Mcts to select
        mc.mcts_training(current_state, times = 1, net = self.net)

        move, state = mc.best_choice_from_root_node()
        self.chessboard = state.chessboard
        self.player = state.player
        self.number_of_steps += 1




    def play(self) :
        """start and keep playing the game until the result coming out"""
        while True :
            self.player_move()
            if self.check_game_result() == ONGOING :
                self.ai_move()
                if self.check_game_result() == BLACK :
                    print('算你厉害')
                    return
                elif self.check_game_result() == WHITE :
                    print('你输了(o^^o)')
                    return
                elif self.check_game_result() == DRAW :
                    print('平局！')
                    return
            elif self.check_game_result() == BLACK :
                print('算你厉害')
                return
            elif self.check_game_result() == WHITE :
                print('你输了(o^^o)')
                return
            elif self.check_game_result() == DRAW :
                print('平局！')
                return
