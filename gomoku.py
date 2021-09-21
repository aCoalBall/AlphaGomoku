from MonteCarloTS import *




class Gomoku :




    def __init__(self) :
        """constructor"""
        self.game_map = [[0 for y in range(15)] for x in range(15)] #the chessboard
        self.current_step = 0 #the current step

    


    def player_move(self, input_by_window=False, pos_x=None, pos_y=None) :
        """player's step"""
        while True :
            try :
                if not input_by_window:
                    pos_x = int(input('x: '))  # 接受玩家的输入人
                    pos_y = int(input('y: '))
                if 0 <= pos_x <= 14 and 0 <= pos_y <= 14 :
                    if self.game_map[pos_x][pos_y] == 0:
                        self.game_map[pos_x][pos_y] = 1
                        self.current_step += 1
                        return
            except ValueError :
                continue
    

    def check_game_result(self, show = False) :
        """return 0 if the game keeps going
           return 1 if the player wins
           return 2 if the AI wins
           return 3 if it's a draw"""
        #1 check horizontal direction
        for x in range(11) :
            for y in range(11) :
                if self.game_map[x+4][y] == 1 and self.game_map[x+3][y] == 1 and self.game_map[x+2][y] == 1 and self.game_map[x+1][y] == 1 and self.game_map[x][y] == 1 :
                    if show :
                        return 1, [(x0, y) for x0 in range(x, x + 5)]
                    else :
                        return 1
                if self.game_map[x+4][y] == 2 and self.game_map[x+3][y] == 2 and self.game_map[x+2][y] == 2 and self.game_map[x+1][y] == 2 and self.game_map[x][y] == 2 :
                    if show :
                        return 2, [(x0, y) for x0 in range(x, x + 5)]
                    else :
                        return 2

        #2 check vertical direction
        for x in range(11) :
            for y in range(11) :
                if self.game_map[x][y] == 1 and self.game_map[x][y+1] == 1 and self.game_map[x][y+2] == 1 and self.game_map[x][y+3] == 1 and self.game_map[x][y+4] == 1 :
                    if show :
                        return 1, [(x, y0) for y0 in range(y, y + 5)]
                    else :
                        return 1
                if self.game_map[x][y] == 2 and self.game_map[x][y+1] == 2 and self.game_map[x][y+2] == 2 and self.game_map[x][y+3] == 2 and self.game_map[x][y+4] == 2 :
                    if show :
                        return 2, [(x, y0) for y0 in range(y, y + 5)]
                    else :
                        return 2

        #3 check from upper-left to lower-right
        for x in range(11) :
            for y in range(11) :
                if self.game_map[x][y+4] == 1 and self.game_map[x+1][y+3] == 1 and self.game_map[x+2][y+2] == 1 and self.game_map[x+3][y+1] == 1 and self.game_map[x+4][y] == 1 :
                    if show :
                        return 1, [(x + t, y + 4 - t) for t in range(5)]
                    else:
                        return 1
                if self.game_map[x][y+4] == 2 and self.game_map[x+1][y+3] == 2 and self.game_map[x+2][y+2] == 2 and self.game_map[x+3][y+1] == 2 and self.game_map[x+4][y] == 2 :
                    if show :
                        return 2, [(x + t, y + 4 - t) for t in range(5)]
                    else:
                        return 2

        #4 check from upper-right to lower-left
        for x in range(11) :
            for y in range(11) :
                if self.game_map[x+4][y+4] == 1 and self.game_map[x+3][y+3] == 1 and self.game_map[x+2][y+2] == 1 and self.game_map[x+1][y+1] == 1 and self.game_map[x][y] == 1 :
                    if show:
                        return 1, [(x + t, y + t) for t in range(5)]
                    else:
                        return 1
                if self.game_map[x+4][y+4] == 2 and self.game_map[x+3][y+3] == 2 and self.game_map[x+2][y+2] == 2 and self.game_map[x+1][y+1] == 2 and self.game_map[x][y] == 2 :
                    if show:
                        return 2, [(x + t, y + t) for t in range(5)]
                    else:
                        return 2
        #5 check if it's a draw
        for x in range(15) :
            for y in range(15) :
                if self.game_map[x][y] == 0 :
                    return 0 , [(-1, -1)]

        if show :
            return 3, [(-1, -1)]
        else:
            return 3




    def ai_move(self) :
        """AI's step"""

        current_state = Board(map = self.game_map, player = 2)
        mc = MonteCarlo()
        mc.mcts_training(current_state, 150)

        self.game_map = mc.best_choice(current_state)[0].game_map
        self.current_step += 1




    def play(self) :
        """start and keep playing the game until the result coming out"""
        while True :
            self.player_move()
            if self.check_game_result() == 0 :
                self.ai_move()
                if self.check_game_result() == 1 :
                    print('算你厉害')
                    return
                elif self.check_game_result() == 2 :
                    print('你输了(o^^o)')
                    return
                elif self.check_game_result() == 3 :
                    print('平局！')
                    return
            elif self.check_game_result() == 1 :
                print('算你厉害')
                return
            elif self.check_game_result() == 2 :
                print('你输了(o^^o)')
                return
            elif self.check_game_result() == 3 :
                print('平局！')
                return
