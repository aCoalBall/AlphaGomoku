from state import State
from global_var import BOARD_SIZE, ONGOING, BLACK, WHITE, DRAW, UNCHECKED

import numpy as np
import copy
import torch


class Node:
    '''the Node class represents nodes in monte carlo tree search'''
    def __init__(self, state, parent):
        self.state = state #the game state for the node
        self.parent = parent #its parent node
        self.status = UNCHECKED #the status of the node, can be ONGOING, BLACK win, WHITE win or DRAW
        self.value = 0 #the value of the current state evaluated by the net
        self.children = {} #all possible moves and the corresponding child nodes
        self.win = 0 #total win times
        self.total = 0 #total access times
    
    def get_ucb(self, ucb_const):
        #get ucb of the node
        if self.total == 0:
            probability = 0
        else:
            probability = self.win / self.total
        ucb = (ucb_const * (probability) * np.sqrt(self.parent.total)) / (1 + self.total)
        return ucb + self.value


class Mcts:
    '''The class of Monte Carlo Tree Search'''
    def __init__(self):
        self.root_node = None #The root node of the tree
        self.current_node = None #The current accessing node
        self.current_move = None #The current move that cause the current state

        self.ucb_const = 1 #The ucb constant
        self.net = None #The neural network
        self.history = [] #the trace of our exploration
    
    def mcts_training(self, state, times, net = None) :
        '''Train via mcts'''
        self.root_node = Node(state, parent = None)
        self.net = net
        for i in range(times) : #Train i times
            self.current_node = self.root_node
            #clear the trace
            self.history = []
            #The following are the 4 phases of mcts
            self.selection()
            self.expansion()
            result = self.simulation()
            self.back_propagation(result)

    def selection(self):
        '''select a new unaccessed node'''
        #selection is the first phase of mcts, which means a new turn of mcts, 
        # init the current state and its parent to the root
        result = self.current_node.state.check_game_result()
        while (result == ONGOING) and (bool(self.current_node.children)):
            self.current_node.status = ONGOING
            #choose the "best" choice given by ucb1
            #track the path of exploration
            self.history.append(self.current_node)
            next_move, next_node  = self.best_choice(self.current_node)
            self.current_node = next_node
            self.current_move = next_move
            result = self.current_node.state.check_game_result()
        #reached an unexplored state, selection is over, now time to expansion
        self.current_node.status = result



    def expansion(self) :
        '''expand new node to the tree'''
        #add the new node to the trace
        self.history.append(self.current_node)
        if self.current_node.status != ONGOING:
            pass
        else:
            #expand the current node and find all its children
            moves_set = self.current_node.state.possible_choices()
            for move in moves_set:
                new_state = copy.deepcopy(self.current_node.state)
                new_state.play(move)
                child_node = Node(state = new_state, parent = self.current_node)
                child_node.value = self.forward_net(child_node, move)
                self.current_node.children[move] = child_node

    def simulation(self) :
        '''evaluate the game trend by net'''
        if self.current_node.status == ONGOING:
            value = self.forward_net(node = self.current_node, move = self.current_move)
            value = value.item()
            if value > 0 : #Better for black player
                return BLACK
            elif value == 0 : #like a draw
                return DRAW
            elif value < 0 : #better for white
                return WHITE
            else :
                pass
        else :
            return self.current_node.status
    
    def back_propagation(self, result) :
        '''update win and total in history nodes'''
        for node in self.history:
            if node.status == ONGOING:
                node.total += 1
        #if black wins    
        if result == BLACK:
            for node in self.history:
                if (node.status == ONGOING) and (node.state.player == BLACK):
                    node.win += 1
        #if white wins 
        if result == WHITE:
            for node in self.history:
                if (node.status == ONGOING) and (node.state.player == WHITE):
                    node.win += 1
        #else, nothing to do

    def best_choice(self, node):
        '''
        Return the node of the best state from the current state
        Also update the children of current node and the parent of the new node
        '''
        if node.status != ONGOING:
            return
        else:
            f = lambda move : node.children[move].get_ucb(self.ucb_const)
            next_move = max(node.children.keys(), key = f)
            return (next_move, node.children[next_move])

    def forward_net(self, node, move):
        '''running the net'''
        state = node.state

        if node.parent == None:
            parent_state = State()
        else:
            parent_state = node.parent.state

        if state.player == BLACK :
            player_state = [[1 for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]
        elif state.player == WHITE :
            player_state = [[2 for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]

        move_state = [[0 for y in range(BOARD_SIZE)] for x in range(BOARD_SIZE)]
        
        if move != None:
            x,y = move
            move_state[x][y] = state.player

        sample = [parent_state.chessboard, state.chessboard, player_state, move_state]
        batch = [sample]
        batch = torch.tensor(batch, dtype=torch.float)
        if torch.cuda.is_available(): 
            batch = batch.cuda()
        value = self.net(batch)
        return value 

    def best_choice_from_root_node(self):
        '''used for self training'''
        move, node = self.best_choice(self.root_node)
        state = node.state
        return move, state





        