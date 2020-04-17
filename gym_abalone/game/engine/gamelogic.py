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

    # NUMBER of life
    LIFES = 6

    def __init__(self):

        self.board = None
        self.positions = None
        self.variant = None
        self.players = 0

        # current
        self.turns_count = None
        self.current_player = None
        self.game_over = False

        # episodes
        self.episode = 0
        self.players_victories = None
    

    def init_game(self, player=0, random_player=True, variant_name='classical', random_pick=False):

        self.board = self.new_board()

        self.positions = AbaloneGame.find_token_coords(self.board, AbaloneGame.TOKEN_EMPTY)
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
        players_sets = self.variant["players_sets"]

        # fill the board
        for p in range(self.players):
            for pos in players_sets[p]:
                r, c = self.positions[pos]
                self.board[r, c] = p
        self.players_damages = [0] * self.players

        # start game counters
        self.turns_count = 1
        self.current_player = np.random.randint(self.players) if random_player else player
        self.game_over = False

        self.episode += 1
        if self.players_victories is None:
            self.players_victories = [0] * self.players

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
    def find_token_coords(board, token):
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

    @staticmethod
    def decompose_directions(r, c):
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
            (tuple): the 3 directions index
        """
        return (r, c, r+c-4)

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

    # =========================================================================
    #                           check methods
    # =========================================================================

    def check_inline_move(self, r0, c0, r1, c1, player, return_modif=True):

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
                action_type = 'inline_move'
                if not return_modif:
                    return action_type
                else:
                    old_positions = [self.get_pos_from_coords(rr, cr) for rr, cr in related]
                    new_positions = [self.get_pos_from_coords(r1, c1)] + old_positions[:-1]
                    modifications = [(old_pos, new_pos, direction_index) 
                                    for old_pos, new_pos in zip(old_positions, new_positions)]
                    return action_type, modifications 
    
    def check_sidestep_move(self, r0, c0, r1, c1, player, return_modif=True):

        dr, dc = r1-r0, c1-c0

        tmp      = [self.decompose_inline(dr-dr1, dc-dc1) for dr1, dc1 in AbaloneGame.ACTIONS]
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
                        action_type = 'sidestep_move'
                        if not return_modif:
                            return action_type
                        else:
                            old_positions = [self.get_pos_from_coords(r_, c_) for r_, c_ in old_coords]
                            new_positions = [self.get_pos_from_coords(r_, c_) for r_, c_ in new_coords]
                            modifications = [(old_pos, new_pos, side_move)  
                                              for old_pos, new_pos in zip(old_positions, new_positions)]
                            return action_type, modifications

    
    def check_inline_push(self, r0, c0, r1, c1, player, return_modif=True):
    
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
            
            # RULE | Sumito : (2vs1) (3vs1) (3vs2)
            # if we seen only 1 player change
            if len(related)==2 and reached:
                if len(related[0])>len(related[1]) and len(related[0])<4:
                    # is a marble ejected
                    ejected = (self.board[r_i, c_i] == AbaloneGame.TOKEN_VOID)
                    action_type = 'ejected' if ejected else 'inline_push'
                    # if we dont need to construct the moves just return True
                    if not return_modif:
                        return action_type
                
                    # flatten the list : allies and enemies will be pushed the same way
                    related = [item for sublist in related for item in sublist][::-1]
                    new_r, new_c = related[0] if ejected else (r_i, c_i)

                    modifications = []
                    if ejected:
                        related.pop(0)
                        # -1 because it is a ejected marble
                        damaged_pos  = self.get_pos_from_coords(new_r, new_c)
                        damage_index = self.players_damages[self.board[new_r, new_c]]
                        modifications += [(damaged_pos, damage_index, -1)] 

                    # simple swap
                    old_positions  = [self.get_pos_from_coords(rr, cr) for rr, cr in related]
                    new_positions  = [self.get_pos_from_coords(new_r, new_c)] + old_positions[:-1]
                    modifications += [(old_pos, new_pos, direction_index) 
                                       for old_pos, new_pos in zip(old_positions, new_positions)]

                    return action_type, modifications
    
    def validate_move(self, pos0, pos1, player, return_modif=False):
        """
        Checks if the move given move (pos0, pos1) is valid
            
        Returns:
            Bool 
        """
        # start pos must be one of the player's marble
        r0, c0 = self.get_coords_from_pos(pos0)
        if self.board[r0, c0] != player:
            return False

        # arrival must be empty or an enemy marble
        r1, c1 = self.get_coords_from_pos(pos1)
        if self.board[r1, c1] == player:
            return False

        # empty spot
        elif self.board[r1, c1] == AbaloneGame.TOKEN_EMPTY:
            # RULE | An "In-line" Move: marbles are moved as a column into a free space
            move_check = self.check_inline_move(r0, c0, r1, c1, player, return_modif=return_modif)
            if move_check:
                return move_check

            # RULE | A 'Side step' move: Marbles are moved sideways into adjacent free spaces.
            move_check = self.check_sidestep_move(r0, c0, r1, c1, player, return_modif=return_modif)
            if move_check:
                return move_check
        
        # enemy marble
        else:
            move_check = self.check_inline_push(r0, c0, r1, c1, player, return_modif=return_modif)
            if move_check:
                return move_check

        return False   

    def get_possible_moves(self, player, group_by_type=False):
        # retrieve start and end pos candidate
        other_pos, player_pos  = [], []
        for pos, (r, c) in enumerate(self.positions):
            (player_pos if self.board[r, c]==player else other_pos).append(pos)

        if group_by_type:
            possibles_moves = {'ejected':[], 'inline_move':[], 'sidestep_move':[], 'inline_push':[]}
        else:
            possibles_moves = []

        for pos0 in player_pos:
            for pos1 in other_pos:
                move_check = self.validate_move(pos0, pos1, player, return_modif=False)
                if move_check:
                    if group_by_type:
                        possibles_moves[move_check].append((pos0, pos1))
                    else:
                        possibles_moves.append((pos0, pos1))

        return possibles_moves

    # =========================================================================
    #                        game modifiers methods
    # =========================================================================

    def next_turn(self):
        self.current_player = (self.current_player + 1) % self.players
        self.turns_count += 1
    
    def swap_coords(self, r0, c0, r1, c1):
        self.board[r0, c0], self.board[r1, c1] = self.board[r1, c1], self.board[r0, c0]

    def eject(self, r, c):
        #print('EJECT')
        damaged_player = self.board[r, c]
        self.players_damages[damaged_player] += 1
        self.board[r, c] = AbaloneGame.TOKEN_EMPTY
        # check if the game is over
        self.game_over = (self.players_damages[damaged_player] == AbaloneGame.LIFES)
        if self.game_over:
            self.players_victories[self.current_player] += 1

    def apply_modifications(self, modifications):
        if not modifications:
            return
        
        for old_pos, new_pos, direction_index in modifications:
            r_old, c_old = self.get_coords_from_pos(old_pos)
            if direction_index == -1: # -1 means that the marble need to be ejected
                self.eject(r_old, c_old)
            else: # otherwise just it's just a swap
                r_new, c_new = self.get_coords_from_pos(new_pos)
                self.swap_coords(r_old, c_old, r_new, c_new)

        self.next_turn()

    # =========================================================================
    #                            ACTION HANDLER
    # =========================================================================

    def action_handler(self, pos0, pos1, return_modif=True):
        assert isinstance(pos0, (int, np.uint8)) and isinstance(pos1, (int, np.uint8))

        # do nothing if the game is over !
        if self.game_over:
            print('GAME OVER !')
            return

        move_check = self.validate_move(pos0, pos1, self.current_player, return_modif=return_modif)
        if move_check:
            move_type, modifications = move_check
            self.apply_modifications(modifications)
            move_type = 'winner' if self.game_over else move_type
            return (move_type, modifications) if return_modif else move_type
        
if __name__ == '__main__':
    AbaloneGame()