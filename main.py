import pyglet
import numpy as np
from pprint import pprint

class window(pyglet.window.Window):

    def __init__(self, width=1100, height=750):

        display = pyglet.canvas.get_display()
        screen = display.get_default_screen()

        screen_width = screen.width
        screen_height = screen.height

        # init the window
        super(window, self).__init__(screen=screen, width=width, height=height, vsync=False)

        # center the window
        x_centered = (screen_width - self.width) // 2
        y_centered = (screen_height - self.height) // 2
        self.set_location(x_centered, y_centered)

        # set the background color to white
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.batch = pyglet.graphics.Batch()

        # create 3 layers
        self.background = pyglet.graphics.OrderedGroup(0)
        self.midleground = pyglet.graphics.OrderedGroup(1)
        self.foreground = pyglet.graphics.OrderedGroup(2)

        self.sprites = []
        board_image = pyglet.image.load('asset/board.png')
        board_sprite = pyglet.sprite.Sprite(board_image, batch=self.batch, group=self.background)
        self.sprites.append(board_sprite)

        black_image = pyglet.image.load('asset/black.png')
        black_sprite = pyglet.sprite.Sprite(black_image, batch=self.batch, group=self.midleground, x=0, y=0)
        #self.sprites.append(black_sprite)

        white_image = pyglet.image.load('asset/white.png')
        white_sprite = pyglet.sprite.Sprite(white_image, batch=self.batch, group=self.midleground, x=320, y=100)
        self.sprites.append(white_sprite)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def start(self):

        # [[-1. -1. -1. -1. -1. -1. -1. -1. -1. -1. -1.]
        #  [-1. -1. -1. -1. -1.  4.  5.  6.  7.  8. -1.]
        #  [-1. -1. -1. -1.  3.  4.  5.  6.  7.  8. -1.]
        #  [-1. -1. -1.  2.  3.  4.  5.  6.  7.  8. -1.]
        #  [-1. -1.  1.  2.  3.  4.  5.  6.  7.  8. -1.]
        #  [-1.  0.  1.  2.  3.  4.  5.  6.  7.  8. -1.]
        #  [-1.  0.  1.  2.  3.  4.  5.  6.  7. -1. -1.]
        #  [-1.  0.  1.  2.  3.  4.  5.  6. -1. -1. -1.]
        #  [-1.  0.  1.  2.  3.  4.  5. -1. -1. -1. -1.]
        #  [-1.  0.  1.  2.  3.  4. -1. -1. -1. -1. -1.]
        #  [-1. -1. -1. -1. -1. -1. -1. -1. -1. -1. -1.]]

        board = np.zeros((11, 11))
        # set border to void
        board[0, :]=board[-1, :]=board[:,0]=board[:,-1] = -1
        # set possible values
        board[1:-1,1:-1] = np.tile(np.arange(9), (9, 1))
        for i in range(4):
            board[1+i, 1:4-i+1] = board[9-i, 6+i:-1] = -1


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

        boxs = [ (r, c) for r in range(11) for c in range(11) if board[r, c] != -1]

        # Actions : possible 
        left      = (0,  -1)
        right     = (0,  +1)
        upleft    = (-1,  0)
        upright   = (-1, +1)
        downleft  = (+1, -1)
        downright = (+1,  0)


    def update(self, dt):
        pass


if __name__ == '__main__':

    main = window()
    main.start()

    pyglet.clock.schedule_interval(main.update, 1 / 60)
    pyglet.app.run()