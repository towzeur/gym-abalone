import numpy as np
from gameutils import AbaloneUtils
 
class AbaloneGame:

    # Actions : possible 
    LEFT       = (0,  -1)
    RIGHT      = (0,  +1)
    UP_LEFT    = (-1,  0)
    UP_RIGHT   = (-1, +1)
    DOWN_LEFT  = (+1, -1)
    DOWN_RIGHT = (+1,  0)

    #   UP_LEFT : 4     5 : UP_RIGHT
    #              \   /
    #               \ /
    # LEFT : 3 ----- * ----- 0 : RIGHT 
    #               /  \ 
    #              /    \ 
    # DOWN_LEFT : 2      1 : DOWN_RIGHT

    ACTIONS = [RIGHT, DOWN_RIGHT, DOWN_LEFT, LEFT, UP_LEFT, UP_RIGHT]

    # tokens
    TOKEN_VOID     = -2
    TOKEN_EMPTY    = -1

    BOARD_SIZE = 11

    def __init__(self):
        self.board = None
        self.positions = None
        self.variant = None
        self.players = 0

        # var for the game logic
        self.players_sets = []
        self.players_damaged_sets = []

        # current
        self.turns_count = 0
        self.current_player = None
        self.current_pos = None
        

    def init_game(self, player=0, random_player=True, variant_name='classical', random_pick=False):

        self.board = self.new_board()

        self.positions = self.find_token_position(self.board, AbaloneGame.TOKEN_EMPTY)
        #                 (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), 
        #             (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), 
        #         (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), 
        #     (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), 
        # (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), 
        #     (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), 
        #         (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), 
        #             (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), 
        #                 (9, 1), (9, 2), (9, 3), (9, 4), (9, 5),
        # 

        self.variant = AbaloneUtils.get_variants(variant_name=variant_name, random_pick=random_pick)
        self.players = self.variant["players"]
        self.players_sets = self.variant["players_sets"]

        # fill the board
        for p in range(self.players):
            for pos in self.players_sets[p]:
                r, c = self.positions[pos]
                self.board[r, c] = p
        self.players_damages = [0 for p in range(self.players)]

        #
        self.current_pos = None
        self.current_player = np.random.randint(self.players) if random_player else player
        self.turns_count = 0

        
    @staticmethod
    def new_board():
        """Example function with types documented in the docstring.

        return a fresh board with no PLAYER_TOKEN

        Returns:
            numpy.ndarray: the new board

        Examples:
            >>> print(AbaloneGame.new_board())
            [[-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1]
             [-1 -1 -1 -1 -1  0  0  0  0  0 -1]
             [-1 -1 -1 -1  0  0  0  0  0  0 -1]
             [-1 -1 -1  0  0  0  0  0  0  0 -1]
             [-1 -1  0  0  0  0  0  0  0  0 -1]
             [-1  0  0  0  0  0  0  0  0  0 -1]
             [-1  0  0  0  0  0  0  0  0 -1 -1]
             [-1  0  0  0  0  0  0  0 -1 -1 -1]
             [-1  0  0  0  0  0  0 -1 -1 -1 -1]
             [-1  0  0  0  0  0 -1 -1 -1 -1 -1]
             [-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1]]
        """
        n = AbaloneGame.BOARD_SIZE
        board = np.full((n, n), AbaloneGame.TOKEN_EMPTY, dtype=np.int8)
        # set border to void
        board[0,:] = board[-1,:] = board[:,0] = board[:,-1] = AbaloneGame.TOKEN_VOID
        for i in range(4):
            board[1+i, 1:4-i+1] = board[n-2-i, 6+i:-1] = AbaloneGame.TOKEN_VOID
        return board

    @staticmethod
    def find_token_position(board, token):
        """ find all the token's position in the given board

        Args:
            param1 (numpy.ndarray): the board
            param1 (int)          : the token to search for

        Returns:
            list: the list with all the position (tuple)
        """
        n = AbaloneGame.BOARD_SIZE
        return [(r, c) for r in range(n) for c in range(n) if board[r, c] == token]

    def get_coords_from_pos(self, pos):
        r, c = self.positions[pos]
        return r, c

    def get_pos_from_coords(self, r, c):
        pos = self.positions.index((r, c))
        return pos

    def get_token_from_pos(self, pos):
        r, c = self.get_coords_from_pos(pos)
        token = self.board[r, c]
        return token

    def get_neighbors(self, r, c):
        return [(r+dr, c+dc) for (dr, dc) in AbaloneGame.ACTIONS]

    def get_neighbors_grouped(self, r, c):
        neighbors_grouped = {}
        for (neighbor_r, neighbor_c) in self.get_neighbors(r, c):
            neighbor_token = self.board[neighbor_r, neighbor_c]
            if neighbor_token not in neighbors_grouped:
                neighbors_grouped[neighbor_token] = []
            neighbors_grouped[neighbor_token].append((neighbor_r, neighbor_c))
        return neighbors_grouped

    def next_turn(self):
        self.current_pos = None
        self.current_player = (self.current_player + 1) % self.players
        self.turns_count += 1

    def _action_change_current_pos(self, pos):
        print('_action_change_current_pos')
        out = {'selected' : (self.current_pos, pos)}
        self.current_pos = pos
        return out

    def _action_move(self, r, c):
        print('_action_move')
        out = {}

        r_curr, c_curr = self.positions[self.current_pos]
        neighbors_curr = self.get_neighbors(r_curr, c_curr)
        
        # print('*', (r_curr, c_curr), (r,c), neighbors_curr)
        # check for single move:
        if (r, c) in neighbors_curr:
            # swap
            self.board[r, c], self.board[r_curr, c_curr] = self.board[r_curr, c_curr], self.board[r, c]
            out['moves'] = [(
                self.get_pos_from_coords(r_curr, c_curr),       # old_pos
                self.get_pos_from_coords(r, c),                 # new pos
                AbaloneGame.ACTIONS.index((r-r_curr, c-c_curr)) # angle direction
            )]
            out['new_turn'] = self.current_pos
            self.next_turn()

        # check for 2 move
        elif False:
            pass

        # check for 3 move
        elif False:
            pass

        return out

    def action_handler(self, pos):
        r, c = self.get_coords_from_pos(pos)
        token = self.board[r, c]

        print(token, self.current_pos, self.current_player)

        # if we clicked on a empty position
        if token == AbaloneGame.TOKEN_EMPTY:
            # is this a missclick ?
            if self.current_pos is None:
                return
            # can the current_pos be moved to the new pos ?
            else:
                return self._action_move(r, c)

        # we clicked on a player
        else:
            # is this the current player ?
            if token == self.current_player:
                return self._action_change_current_pos(pos)
            # this a another player position
            else:
                pass



if __name__ == '__main__':

    
    AbaloneGame()







