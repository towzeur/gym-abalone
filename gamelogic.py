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

    ACTIONS_NAME = ['→', '↘', '↙', '←', '↖', '↗']

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
        self.turns_count = None
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

        # start game counters
        self.turns_count = 0
        self.current_player = np.random.randint(self.players) if random_player else player
        self.current_pos = None

    # =========================================================================
    #                           BOARD RELATED 
    # =========================================================================
        
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

    @staticmethod
    def get_neighbors(r, c):
        return [(r+dr, c+dc) for (dr, dc) in AbaloneGame.ACTIONS]

    # =========================================================================
    #                           GAME RELATED 
    # =========================================================================

    def next_turn(self):
        self.current_pos = None
        self.current_player = (self.current_player + 1) % self.players
        self.turns_count += 1

    @staticmethod
    def check_inline_move(dr, dc):
        """
        In Abalone, there is 3 directions :
        (RIGHT-LEFT) | (DOWN_RIGHT-UP_LEFT) | (DOWN_LEFT-UP_RIGHT)
        (←    -   →) | (↙        -       ↗) | (↙       -        ↗)

        Checks if the move given by dr (detla row) and dc (delta col) 
        follows a unique direction move. If this is the case, it returns 
        the step taken in such direction. Otherwise it returns None.
            
        Returns:
            tuple (step, direction_index)
                step            : the number of step in the direction
                direction_index : the index of the direction (0< <=5)
            None 
                if the deplacement is not in a unique direction

        Examples:
            >>> print(AbaloneGame.check_inline_move(1, 0))
            (1, 1)
            >>> print(AbaloneGame.check_inline_move(-3, 3))
            (3, 5)
            >>> print(AbaloneGame.check_inline_move(2, -1))
            None
        """
        # RIGHT or LEFT
        if dr==0:
            return (np.abs(dc), 0 if np.sign(dc)==1 else 3)
        # DOWN_RIGHT or UP_LEFT
        elif dc==0:
            return (np.abs(dr), 1 if np.sign(dr)==1 else 4)
        # DOWN_LEFT or UP_RIGHT
        elif np.abs(dr)==np.abs(dc) and np.sign(dr)!=np.sign(dc):
            return (np.abs(dr), 2 if np.sign(dr)==1 else 5)
    
    def swap_coords(self, r0, c0, r1, c1):
        self.board[r0, c0], self.board[r1, c1] = self.board[r1, c1], self.board[r0, c0]

    def swap_many_coords(self, new_r, new_c, old_coords, direction_index):
        # push the marbles
        out = []
        for old_r, old_c in old_coords:
            # swap
            self.swap_coords(old_r, old_c, new_r, new_c)
            # log the move for GUI
            out.append((
                self.get_pos_from_coords(old_r, old_c),
                self.get_pos_from_coords(new_r, new_c),
                direction_index
            ))
            new_r, new_c = old_r, old_c
        return out
    
    def eject(self, r, c):
        print('EJECT')
        damaged_player = self.board[r, c]
        # log for GUI
        out = (self.get_pos_from_coords(r, c), self.players_damages[damaged_player])
        self.players_damages[damaged_player] += 1
        self.board[r, c] = AbaloneGame.TOKEN_EMPTY
        return out

    # =========================================================================
    #                            ACTION HANDLER
    # =========================================================================

    def _action_change_current_pos(self, pos):
        print('_action_change_current_pos')
        out = {'selected' : (self.current_pos, pos)}
        self.current_pos = pos
        return out

    def _action_move(self, r, c):
        print('_action_move')

        out = {}
        r_curr, c_curr = self.positions[self.current_pos]
        dr, dc = r-r_curr, c-c_curr

        # =========================================================================
        # RULE | An "In-line" Move: marbles are moved as a column into a free space
        # =========================================================================
        inline = self.check_inline_move(dr, dc)
        if inline:
            step, direction_index = inline
            r_step, c_step = AbaloneGame.ACTIONS[direction_index]

            print(f'dr={dr} dc={dc} | {step}{AbaloneGame.ACTIONS_NAME[direction_index]}')

            # =====================================================================
            # RULE | At any turn, no more than 3 friendly marbles can be moved
            # =====================================================================
            if step > 3:
                return out
     
            # find the related neighbors in the direction
            related = [(r_curr+n*r_step, c_curr+n*c_step) for n in reversed(range(step))]

            # if the all the related marbles belongs to the same player
            if all([self.board[rr, cr] == self.current_player for rr, cr in related]):
                out['moves'] = self.swap_many_coords(r, c, related, direction_index)
                out['new_turn'] = self.current_pos
                self.next_turn()

        # =========================================================================
        # RULE | A 'Side step' move: Marbles are moved sideways into adjacent free spaces.
        # ========================================================================= 
        else:
            pass

        return out

    def _action_push(self, r, c):
        print('_action_push')

        out = {}
        r_curr, c_curr = self.positions[self.current_pos]
        dr, dc = r-r_curr, c-c_curr

        inline = self.check_inline_move(dr, dc)
        if inline:
            step, direction_index = inline
            r_step, c_step = AbaloneGame.ACTIONS[direction_index]
            print(f'dr={dr} dc={dc} | {step}{AbaloneGame.ACTIONS_NAME[direction_index]}')

            # validate the move : find the free spot
            related = [[(r_curr, c_curr)]]
            r_i, c_i = r_curr + r_step , c_curr +  c_step
            reached = False
            prev_player = self.current_player
            while self.board[r_i, c_i] not in [AbaloneGame.TOKEN_EMPTY, AbaloneGame.TOKEN_VOID]:
                if self.board[r_i, c_i] == prev_player:
                    related[-1].append((r_i, c_i))
                else:
                    related.append([(r_i, c_i)])
                    prev_player = self.board[r_i, c_i]
                if (r_i, c_i) == (r, c):
                    reached = True
                r_i, c_i = r_i + r_step , c_i +  c_step
            print('_', reached, related, [len(x) for x in related])
            
            if len(related)==2 and reached:
                # =========================================================================
                # RULE | Sumito : (2vs1) (3vs1) (3vs2)
                # ========================================================================= 
                if len(related[0])>len(related[1]) and len(related[0])<4:
                    print('PUSHED')
                    related = [item for sublist in related for item in sublist][::-1]
       
                    # check if we need to eject a marble
                    ejected = (self.board[r_i, c_i] == AbaloneGame.TOKEN_VOID)
                    r_ejc, c_ejc = related[0]
                    if ejected:
                        related.pop(0)
                        out['damage'] = self.eject(r_ejc, c_ejc)

                    # push the marbles
                    new_r, new_c = (r_ejc, c_ejc) if ejected else (r_i, c_i)
                    out['moves'] = self.swap_many_coords(new_r, new_c, related, direction_index)
                    out['new_turn'] = self.current_pos
                    self.next_turn()

        return out

    def action_handler(self, pos):
        r, c = self.get_coords_from_pos(pos)
        token = self.board[r, c]
        #print(token, self.current_pos, self.current_player)

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
            elif self.current_pos is not None:
                return self._action_push(r, c)

if __name__ == '__main__':
    AbaloneGame()