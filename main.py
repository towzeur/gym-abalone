import pyglet
from pyglet.window import key
import numpy as np
from pprint import pprint
import time
import json

from gamelogic import AbaloneGame
from gameutils import AbaloneUtils

class window(pyglet.window.Window):

    def __init__(self, theme="default"):

        # set the theme
        self.theme = AbaloneUtils.get_theme(theme)

        # init the game engine
        self.game = AbaloneGame()

        width  = self.theme['dimension']['width']
        height = self.theme['dimension']['height']

        display = pyglet.canvas.get_display()
        screen = display.get_default_screen()

        screen_width = screen.width
        screen_height = screen.height

        # init the window's constructor
        super(window, self).__init__(screen=screen, width=width, height=height, vsync=False)

        # center the window
        x_centered = (screen_width - self.width) // 2
        y_centered = (screen_height - self.height) // 2
        self.set_location(x_centered, y_centered)

        # set the background color to white
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.batch = pyglet.graphics.Batch()

        # create layers
        self.groups = [pyglet.graphics.OrderedGroup(i) for i in range(3)]

        # display the background 
        board_image = pyglet.image.load(self.theme['sprites']['board'])
        self.board_sprite = pyglet.sprite.Sprite(board_image, batch=self.batch, group=self.groups[0])
        
        self.players_cells = None

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def init_window(self, debug=True):

        # reset the game
        self.game.init_game(random_pick=True)

        # reset players's sprites
        if self.players_cells:
            for player_cells in self.players_cells:
                for cell in player_cells:
                    cell['sprite'].delete()
                    if 'pos_text' in cell:
                        cell['pos_text'].delete()
                    del cell
        self.players_cells = None

        # draw the board for the first time
        self.draw_board(debug)

    def draw_token(self, pos, player=1, debug=True):
        cell = {}

        # compute the coords from the pos
        x, y = self.theme['coordinates'][pos]

        # select the right player image
        im_path = self.theme['sprites']['players'][player-1]

        # create the sprite
        im = pyglet.image.load(im_path)
        cell['sprite'] = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[1], x=x, y=y)

        if debug:
            cell['pos_text'] = pyglet.text.Label(
                f'{pos}', x=x, y=y,
                font_name='Roboto',
                font_size=28,
                color=(0, 0, 0, 255) if player==1 else (255, 255, 255, 255),
                anchor_x='left', anchor_y='bottom',
                batch=self.batch,
                group=self.groups[2]
            )

        return cell

    def draw_board(self, debug=True):
        self.players_cells = [[] for p in range(self.game.players)]
        for p in range(self.game.players):
            TOKEN_PLAYER = p + 1
            for pos in self.game.players_sets[p]:
                cell = self.draw_token(pos, player=TOKEN_PLAYER, debug=debug)
                self.players_cells[p].append(cell)

    def update(self, dt):
        self.init_window(debug=False)
        return 

    def on_mouse_press(self, x, y, button, modifiers):
        print(x, y)
    
    def on_key_press(self, symbol, modifiers):
        
        tmp = {
            key.LEFT  : (-1, 0),
            key.RIGHT : (+1, 0),
            key.DOWN  : (0, -1),
            key.UP    : (0, +1)
        }

        i = 1

        if symbol in tmp:
            self.init_window()
            return

            '''
            x, y = self.locations[i].position
            dx, dy = tmp[symbol]
            new_x, new_y = x+dx, y+dy
            self.locations[i].update(x=new_x, y=new_y)
            print(new_x, new_y)
            '''

if __name__ == '__main__':

    main = window()
    main.init_window()
    pyglet.clock.schedule_interval(main.update, 1)
    pyglet.app.run()