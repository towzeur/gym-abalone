import numpy as np
from ..common.gameutils import AbaloneUtils
 
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

    LIFES = 6

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
        self.game_over = False
        

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
        self.game_over = False

    # =========================================================================
    #                           BOARD RELATED 
    # =========================================================================
        
    @staticmethod
    def new_board():
        """
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

    
    def decompose_directions(self, r, c):
        r"""
        return the decomposition of (r, c) in the 3 directions

        0      - - - - -      |      \ \ \ \ \       |        / / / / /
        1     - - - - - -     |     \ \ \ \ \ \      |       / / / / / /
        2    - - - - - - -    |    \ \ \ \ \ \ \     |      / / / / / / / 
        3   - - - - - - - -   |   \ \ \ \ \ \ \ \    |     / / / / / / / /
        4  - - - - - - - - -  |  \ \ \ \ \ \ \ \ \   |    / / / / / / / / /
        5   - - - - - - - -   |   \ \ \ \ \ \ \ \ 8  |   0 / / / / / / / / 
        6    - - - - - - -    |    \ \ \ \ \ \ \ 7   |    1 / / / / / / /
        7     - - - - - -     |     \ \ \ \ \ \ 6    |     2 / / / / / /
        8      - - - - -      |      \ \ \ \ \ 5     |      3 / / / / /
                              |       0 1 2 3 4      |       4 5 6 7 8

        Args:
            r (int) : the board
            c (int) : the token to search for

        Returns:
            (tuple): the list with all the position (tuple)
        """
        return (r, c, r+c-4)


    # =========================================================================
    #                           GAME RELATED 
    # =========================================================================

    def next_turn(self):
        self.current_pos = None
        self.current_player = (self.current_player + 1) % self.players
        self.turns_count += 1


    @staticmethod
    def decompose_inline(dr, dc):
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
            >>> print(AbaloneGame.decompose_inline(1, 0))
            (1, 1)
            >>> print(AbaloneGame.decompose_inline(-3, 3))
            (3, 5)
            >>> print(AbaloneGame.decompose_inline(2, -1))
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

    
    def check_inline_move(self, r0, c0, r1, c1, player, return_action=True):

        dr, dc = r1-r0, c1-c0
        inline_distance = self.decompose_inline(dr, dc)
        # if aligned
        if inline_distance:
            step, direction_index = inline_distance
            r_step, c_step = AbaloneGame.ACTIONS[direction_index]
            #print(f'dr={dr} dc={dc} | {step}{AbaloneGame.ACTIONS_NAME[direction_index]}')
            # RULE | At any turn, no more than 3 friendly marbles can be moved
            if step > 3:
                return
            # find the related neighbors in the direction
            related = [(r0+n*r_step, c0+n*c_step) for n in reversed(range(step))]
            # if all the related marbles belongs to the same player
            if all([self.board[rr, cr] == self.current_player for rr, cr in related]):

                if not return_action:
                    return True

                out={}
                # log : moves
                old_positions = [self.get_pos_from_coords(rr, cr) for rr, cr in related]
                new_positions = [self.get_pos_from_coords(r1, c1)] + old_positions[:-1]
                out['moves'] = [(old_pos, new_pos, direction_index)  
                                for old_pos, new_pos in zip(old_positions, new_positions)]
                # log : new_turn
                out['new_turn'] = self.get_pos_from_coords(r0, c0)
                print('*FALG**', out)
                return out
        
    
    def check_sidestep_move(self, r0, c0, r1, c1, player, return_action=True):

        dr, dc = r1-r0, c1-c0

        tmp      = [self.decompose_inline(dr-dr1, dc-dc1) for dr1, dc1 in self.ACTIONS]
        decomp_0 = self.decompose_directions(r0, c0)
        decomp_1 = self.decompose_directions(r1, c1)
        decomp   = [a-b for a,b in zip(decomp_1, decomp_0)]

        for i in range(len(decomp)):
            direction_distance = decomp[i]
            # if the direction are 1 deplacement appart
            if np.abs(direction_distance)==1:

                # reach the direction
                act_p = ((1,2), (0,5), (0,1)) # positive
                act_n = ((4,5), (3,2), (3,4)) # negative
                
                # there is 2 way of teaching it, take the right one
                sm0, sm1 = act_p[i] if direction_distance>0 else act_n[i]
                # 1 step sideway
                side_move = sm0 if (tmp[sm0][0]<tmp[sm1][0]) else sm1
                dr_step, dc_step = AbaloneGame.ACTIONS[side_move]

                # inline move
                inline_step, inline_move = tmp[side_move]
                dr_inline, dc_inline = AbaloneGame.ACTIONS[inline_move]

                # At any turn, no more than 3 friendly marbles can be moved
                if inline_step < 3:
                    old_coords = [(r0+dr_inline*s, c0+dc_inline*s) for s in range(inline_step+1)]
                    new_coords = [(r0+dr_step+dr_inline*s, c0+dc_step+dc_inline*s) for s in range(inline_step+1)]
                    
                    connected = all(self.board[r_, c_] == player for (r_, c_) in old_coords)
                    free      = all(self.board[r_, c_] == AbaloneGame.TOKEN_EMPTY for (r_, c_) in new_coords)
                    
                    if connected and free:
                        #print(AbaloneGame.ACTIONS_NAME[side_move], inline_step, AbaloneGame.ACTIONS_NAME[inline_move])
                        if not return_action:
                            return True
                        out= {}
                        # log moves
                        old_positions = [self.get_pos_from_coords(r_, c_) for r_, c_ in old_coords]
                        new_positions = [self.get_pos_from_coords(r_, c_) for r_, c_ in new_coords]
                        out['moves'] = [(old_pos, new_pos, side_move)  
                                        for old_pos, new_pos in zip(old_positions, new_positions)]
                        # log : new_turn
                        out['new_turn'] = self.get_pos_from_coords(r0, c0)
                        return out

    
    def check_inline_push(self, r0, c0, r1, c1, player, return_action=True):
    
        dr, dc = r1-r0, c1-c0
        inline = self.decompose_inline(dr, dc)
        if inline:
            step, direction_index = inline
            r_step, c_step = AbaloneGame.ACTIONS[direction_index]
            #print(f'dr={dr} dc={dc} | {step}{AbaloneGame.ACTIONS_NAME[direction_index]}')

            # 3vs2 is the max so 3+2-1=4 is the max distance
            if step>4: 
                return

            # validate the move : find the free spot
            related = [[(r0, c0)]]
            r_i, c_i = r0 + r_step , c0 +  c_step
            reached = False
            prev_player = player
            while self.board[r_i, c_i] not in [AbaloneGame.TOKEN_EMPTY, AbaloneGame.TOKEN_VOID]:
                if self.board[r_i, c_i] == prev_player:
                    related[-1].append((r_i, c_i))
                else:
                    related.append([(r_i, c_i)])
                    prev_player = self.board[r_i, c_i]
                if (r_i, c_i) == (r1, c1):
                    reached = True
                r_i, c_i = r_i + r_step , c_i +  c_step
            #print('_', reached, related, [len(x) for x in related])
            
            # =========================================================================
            # RULE | Sumito : (2vs1) (3vs1) (3vs2)
            # ========================================================================= 
            # if we seen only 1 player change
            if len(related)==2 and reached:
                if len(related[0])>len(related[1]) and len(related[0])<4:

                    # if we dont need to construct the moves just return True
                    if not return_action:
                        return True
                    
                    out = {}
                    # flatten the list : allies and enemies will be pushed the same way
                    related = [item for sublist in related for item in sublist][::-1]
    
                    # check if we need to eject a marble :
                    # the last pos is the void
                    ejected = (self.board[r_i, c_i] == AbaloneGame.TOKEN_VOID)
                    new_r, new_c = related[0] if ejected else (r_i, c_i)
                    if ejected:
                        related.pop(0)
                        # log the removed marble
                        out['damage'] = (self.get_pos_from_coords(new_r, new_c), 
                                         self.players_damages[self.board[new_r, new_c]])

                    # log : MOVES
                    old_positions = [self.get_pos_from_coords(rr, cr) for rr, cr in related]
                    new_positions = [self.get_pos_from_coords(new_r, new_c)] + old_positions[:-1]
                    out['moves'] = [(old_pos, new_pos, direction_index) 
                                     for old_pos, new_pos in zip(old_positions, new_positions)]

                    # log : new_turn
                    out['new_turn'] = self.get_pos_from_coords(r0, c0)

                    return out
    
    def validate_move(self, pos0, pos1, player):
        #r0, c0 = self.get_coords_from_pos(pos0)
        #r1, c1 = self.get_coords_from_pos(pos1)
        #check_sidestep_move
        pass
    
    def swap_coords(self, r0, c0, r1, c1):
        self.board[r0, c0], self.board[r1, c1] = self.board[r1, c1], self.board[r0, c0]

    def swap_pos_lists(self, old_positions, new_positions):
        for old_pos, new_pos in zip(old_positions, new_positions):
            r_old, c_old = self.get_coords_from_pos(old_pos)
            r_new, c_new = self.get_coords_from_pos(new_pos)
            self.swap_coords(r_old, c_old, r_new, c_new)

    def eject(self, r, c):
        #print('EJECT')
        damaged_player = self.board[r, c]
        self.players_damages[damaged_player] += 1
        self.board[r, c] = AbaloneGame.TOKEN_EMPTY
        # check if the game is over
        self.game_over = any(life == AbaloneGame.LIFES for life in self.players_damages) 

    # =========================================================================
    #                            ACTION HANDLER
    # =========================================================================

    def apply_modifications(self, modifications):
        print(modifications)
        if 'selected' in modifications:
            self.current_pos = modifications['selected'][1]

        if 'damage' in modifications:
            pos_ejected = modifications['damage'][0]
            r_ejected, c_ejected = self.get_coords_from_pos(pos_ejected)
            self.eject(r_ejected, c_ejected)

        if 'moves' in modifications:
            
            old_positions = [m[0] for m in modifications['moves']]
            new_positions = [m[1] for m in modifications['moves']]

            print('flag2', old_positions, new_positions)

            self.swap_pos_lists(old_positions, new_positions)

        if 'new_turn' in modifications:
            self.next_turn()

    def _action_change_current_pos(self, pos):
        #print('_action_change_current_pos')
        modifications = {'selected' : (self.current_pos, pos)}
        self.apply_modifications(modifications)
        return modifications

    def _action_move(self, r, c):
        #print('_action_move')
        r_curr, c_curr = self.positions[self.current_pos]
        # =========================================================================
        # RULE | An "In-line" Move: marbles are moved as a column into a free space
        # =========================================================================
        modifications = self.check_inline_move(r_curr, c_curr, r, c, self.current_player)
        if modifications:
            print('inline modifications')
            self.apply_modifications(modifications)
            return modifications
        # =========================================================================
        # RULE | A 'Side step' move: Marbles are moved sideways into adjacent free spaces.
        # ========================================================================= 
        else:
            modifications = self.check_sidestep_move(r_curr, c_curr, r, c, self.current_player)
            if modifications:
                print('side step modifications')
                self.apply_modifications(modifications)
                return modifications

    def _action_push(self, r, c):
        #print('_action_push')
        r_curr, c_curr = self.positions[self.current_pos]
        modifications = self.check_inline_push(r_curr, c_curr, r, c, self.current_player)
        if modifications:
            self.apply_modifications(modifications)
            return modifications

    def action_handler(self, pos):
        # do nothing if the game is over !
        if self.game_over:
            print('GAME OVER !')
            return

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