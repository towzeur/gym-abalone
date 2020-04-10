import numpy as np


class AbaloneGame:

    # Actions : possible 
    LEFT       = (0,  -1)
    RIGHT      = (0,  +1)
    UP_LEFT    = (-1,  0)
    UP_RIGHT   = (-1, +1)
    DOWN_LEFT  = (+1, -1)
    DOWN_RIGHT = (+1,  0)

    ACTIONS = [LEFT, RIGHT, UP_LEFT, UP_RIGHT, DOWN_LEFT, DOWN_RIGHT]

    # tokens
    TOKEN_VOID     = -1
    TOKEN_EMPTY    =  0
    TOKEN_PLAYER_1 =  1
    TOKEN_PLAYER_2 =  2

    BOARD_SIZE = 11

    def __init__(self):
        
        self.board = self.new_board()
        print(self.board)

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

        print(self.positions)
        print(len(self.positions))

    @staticmethod
    def new_board():
        """Example function with types documented in the docstring.

        return a fresh board with no PLAYER_TOKEN

        Returns:
            numpy.ndarray: the new board

        Examples:
            >>> print(AbaloneGame.new())
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


if __name__ == '__main__':

    
    AbaloneGame()







