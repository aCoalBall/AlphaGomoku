from global_var import BOARD_SIZE, ONGOING, BLACK, WHITE, DRAW, UNCHECKED

'''
The class that record the current state of a game. It contains 2 variable: 
chessboard, which records the state of the chessboard,
and player, that records it is which player's turn currently.
'''
class State:

    def __init__(self, chessboard = None, player = None) :
        """constructor"""
        #set the chessboard
        if chessboard == None :
            self.chessboard = [[0 for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)] 
        else :
            self.chessboard = chessboard
        ##set the player    
        if player == None :
            self.player = BLACK
        else :
            self.player = player
    
    def check_game_result(self) :
        """return 0 if the game keeps going
           return 1 if the BLACK wins
           return 2 if the WHITE wins
           return 3 if it's a draw"""
        #1 check horizontal direction
        for x in range(BOARD_SIZE - 4) :
            for y in range(BOARD_SIZE - 4) :
                if self.chessboard[x+4][y] == 1 and self.chessboard[x+3][y] == 1 and self.chessboard[x+2][y] == 1 and self.chessboard[x+1][y] == 1 and self.chessboard[x][y] == 1 :
                    return BLACK
                if self.chessboard[x+4][y] == 2 and self.chessboard[x+3][y] == 2 and self.chessboard[x+2][y] == 2 and self.chessboard[x+1][y] == 2 and self.chessboard[x][y] == 2 :
                    return WHITE

        #2 check vertical direction
        for x in range(BOARD_SIZE - 4) :
            for y in range(BOARD_SIZE - 4) :
                if self.chessboard[x][y] == 1 and self.chessboard[x][y+1] == 1 and self.chessboard[x][y+2] == 1 and self.chessboard[x][y+3] == 1 and self.chessboard[x][y+4] == 1 :
                    return BLACK
                if self.chessboard[x][y] == 2 and self.chessboard[x][y+1] == 2 and self.chessboard[x][y+2] == 2 and self.chessboard[x][y+3] == 2 and self.chessboard[x][y+4] == 2 :
                    return WHITE

        #3 check from upper-left to lower-right
        for x in range(BOARD_SIZE - 4) :
            for y in range(BOARD_SIZE - 4) :
                if self.chessboard[x][y+4] == 1 and self.chessboard[x+1][y+3] == 1 and self.chessboard[x+2][y+2] == 1 and self.chessboard[x+3][y+1] == 1 and self.chessboard[x+4][y] == 1 :
                    return BLACK
                if self.chessboard[x][y+4] == 2 and self.chessboard[x+1][y+3] == 2 and self.chessboard[x+2][y+2] == 2 and self.chessboard[x+3][y+1] == 2 and self.chessboard[x+4][y] == 2 :
                    return WHITE

        #4 check from upper-right to lower-left
        for x in range(BOARD_SIZE - 4) :
            for y in range(BOARD_SIZE - 4) :
                if self.chessboard[x+4][y+4] == 1 and self.chessboard[x+3][y+3] == 1 and self.chessboard[x+2][y+2] == 1 and self.chessboard[x+1][y+1] == 1 and self.chessboard[x][y] == 1 :
                    return BLACK
                if self.chessboard[x+4][y+4] == 2 and self.chessboard[x+3][y+3] == 2 and self.chessboard[x+2][y+2] == 2 and self.chessboard[x+1][y+1] == 2 and self.chessboard[x][y] == 2 :
                    return WHITE
        #5 check if it's a draw
        for x in range(BOARD_SIZE) :
            for y in range(BOARD_SIZE) :
                if self.chessboard[x][y] == 0 :
                    return ONGOING
        return DRAW

    def possible_choices(self):
        """
        Returns an iterable set of all choices(moves) which can be taken from this state
        """
        #If the game is on-going
        if self.check_game_result() == ONGOING :
            legal = set()
            #Check all empty(that is, valid) positions
            for x in range(BOARD_SIZE) :
                for y in range(BOARD_SIZE) :
                    if self.chessboard[x][y] == 0 :
                        legal.add((x,y))
            #If its an empty board
            if len(legal) == BOARD_SIZE * BOARD_SIZE:
                return legal
            #If not empty
            else:
                limited_legal = set()
                for m in legal :
                    x,y = m
                    min_x = max(0, x - 3)
                    max_x = min(BOARD_SIZE - 1, x + 3)
                    min_y = max(0, y - 3)
                    max_y = min(BOARD_SIZE - 1, y + 3)
                    ranges = set()
                    for xr in range(min_x, max_x + 1):
                        for yr in range(min_y, max_y + 1):
                            ranges.add((xr,yr))
                    for xr,yr in ranges:
                        if self.chessboard[xr][yr] != 0 :
                            limited_legal.add((x,y))
                            break
                return limited_legal
        else :
            return set()

    def play(self, action):
        '''
       Put a chess piece on the board.
        '''
        pos_x, pos_y = action
        if 0 <= pos_x <= BOARD_SIZE - 1 and 0 <= pos_y <= BOARD_SIZE - 1 :
            if self.player == BLACK :
                if self.chessboard[pos_x][pos_y] == 0:
                    self.chessboard[pos_x][pos_y] = 1
                    self.player = WHITE
                    return
            elif self.player == WHITE :
                if self.chessboard[pos_x][pos_y] == 0:
                    self.chessboard[pos_x][pos_y] = 2
                    self.player = BLACK
                    return
        else :
            return

