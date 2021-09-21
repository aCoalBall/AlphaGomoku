from gomoku import *
import random
import copy
import math

BLACK = 1
WHITE = 2

STATUS = 0
WINNING_RATE = 1
ALL_MOVES = 2

class Board :

    def __init__(self, map = None, player = None) :
        """constructor"""
        if map == None :
            self.game_map = [[0 for y in range(15)] for x in range(15)] #the chessboard
        else :
            self.game_map = map

        if player == None :
            self.player = BLACK
        else :
            self.player = player

    def __hash__(self) :
        return hash(tuple(item for sublist in self.game_map for item in sublist) + (self.player,))
    
    def __eq__(self, other) :
        return tuple(item for sublist in self.game_map for item in sublist) == \
            tuple(item for sublist in other.game_map for item in sublist) and \
                self.player == other.player


    def play(self, pos_x, pos_y) :
        if 0 <= pos_x <= 14 and 0 <= pos_y <= 14 :
            if self.player == BLACK :
                if self.game_map[pos_x][pos_y] == 0:
                    self.game_map[pos_x][pos_y] = 1
                        
                    self.player = WHITE
                    return
            elif self.player == WHITE :
                if self.game_map[pos_x][pos_y] == 0:
                    self.game_map[pos_x][pos_y] = 2

                    self.player = BLACK
                    return
        else :
            return

            
    def possible_choices(self) :
        """
        if self.check_game_result() == 0 :
            legal = set()
            for x in range(15) :
                for y in range(15) :
                    if self.game_map[x][y] == 0 :
                        legal.add((x,y))
            return legal
        else :
            return set()
        """
        if self.check_game_result() == 0 :
            legal = set()
            for x in range(15) :
                for y in range(15) :
                    if self.game_map[x][y] == 0 :
                        legal.add((x,y))
            if len(legal) == 225:
                return legal
            else:
                limited_legal = set()
                for m in legal :
                    x,y = m
                    min_x = max(0, x - 3)
                    max_x = min(14, x + 3)
                    min_y = max(0, y - 3)
                    max_y = min(14, y + 3)
                    ranges = set()
                    for xr in range(min_x, max_x + 1):
                        for yr in range(min_y, max_y + 1):
                            ranges.add((xr,yr))
                    for xr,yr in ranges:
                        if self.game_map[xr][yr] != 0 :
                            limited_legal.add((x,y))
                            break
                return limited_legal
                
        else :
            return set()


    def check_game_result(self) :
        """return 0 if the game keeps going
           return 1 if the BLACK wins
           return 2 if the WHITE wins
           return 3 if it's a draw"""
        #1 check horizontal direction
        for x in range(11) :
            for y in range(11) :
                if self.game_map[x+4][y] == 1 and self.game_map[x+3][y] == 1 and self.game_map[x+2][y] == 1 and self.game_map[x+1][y] == 1 and self.game_map[x][y] == 1 :
                    return 1
                if self.game_map[x+4][y] == 2 and self.game_map[x+3][y] == 2 and self.game_map[x+2][y] == 2 and self.game_map[x+1][y] == 2 and self.game_map[x][y] == 2 :
                    return 2

        #2 check vertical direction
        for x in range(11) :
            for y in range(11) :
                if self.game_map[x][y] == 1 and self.game_map[x][y+1] == 1 and self.game_map[x][y+2] == 1 and self.game_map[x][y+3] == 1 and self.game_map[x][y+4] == 1 :
                    return 1
                if self.game_map[x][y] == 2 and self.game_map[x][y+1] == 2 and self.game_map[x][y+2] == 2 and self.game_map[x][y+3] == 2 and self.game_map[x][y+4] == 2 :
                    return 2

        #3 check from upper-left to lower-right
        for x in range(11) :
            for y in range(11) :
                if self.game_map[x][y+4] == 1 and self.game_map[x+1][y+3] == 1 and self.game_map[x+2][y+2] == 1 and self.game_map[x+3][y+1] == 1 and self.game_map[x+4][y] == 1 :
                    return 1
                if self.game_map[x][y+4] == 2 and self.game_map[x+1][y+3] == 2 and self.game_map[x+2][y+2] == 2 and self.game_map[x+3][y+1] == 2 and self.game_map[x+4][y] == 2 :
                    return 2

        #4 check from upper-right to lower-left
        for x in range(11) :
            for y in range(11) :
                if self.game_map[x+4][y+4] == 1 and self.game_map[x+3][y+3] == 1 and self.game_map[x+2][y+2] == 1 and self.game_map[x+1][y+1] == 1 and self.game_map[x][y] == 1 :
                    return 1
                if self.game_map[x+4][y+4] == 2 and self.game_map[x+3][y+3] == 2 and self.game_map[x+2][y+2] == 2 and self.game_map[x+1][y+1] == 2 and self.game_map[x][y] == 2 :
                    return 2
        #5 check if it's a draw
        for x in range(15) :
            for y in range(15) :
                if self.game_map[x][y] == 0 :
                    return 0

        return 3