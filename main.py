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

    def init_window(self, variant_name='classical', random_pick=True, debug=True):

        # reset the game
        self.game.init_game(variant_name=variant_name, random_pick=random_pick)

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
        self.draw_board(debug=debug)

    def draw_token(self, pos, player=1, debug=True):
        cell = {
            'pos':pos,
            'out':False
        }

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
        print(f'({x}, {y})')
        pos = self.is_marbles_clicked(x, y)
        if pos != -1:
            player_token = self.game.action(pos)
            player = player_token - 1
            # find the cell
            for cell in self.players_cells[player]:
                if cell['pos'] == pos:
                    damage_index = self.game.players_damages[player]
                    new_x, new_y = self.theme['out_coordinates'][player][damage_index]
                    cell['sprite'].update(x=new_x, y=new_y)
                    # increase damage
                    self.game.players_damages[player] += 1
                    break
            




    def is_marbles_clicked(self, x, y):
        """
        return the pos of the clicked marble.
        
        It do so by starting in the first row and increse the col.
        It's a bit better than bruteforce because it skips the current row if the 
        first elt (first column) is not within the outter box.
        if the click is find inside a box, it compute the L2 norm to find
        if the click is inded upon the marble.

        Returns:
            (int) pos : pos of the clicked marble if it exists (0 < pos < self.theme['locations'] )
            (int)  -1 : otherwise
        """

        R = self.theme['dimension']['marble_radius']
        C = R * 2

        pos = 0
        for row, nb_col in enumerate(self.theme['rows']):
            for col in range(nb_col):
                x_bot_left, y_bot_left = self.theme['coordinates'][pos]
                # we first start by checking if the click is in the circle's outter box
                # are we in the right row ?
                if 0 <= (y -  y_bot_left) <= C:
                    # then if a solution exist it may be on this row
                    # is it on this box ?
                    if 0 <= (x -  x_bot_left) <= C:
                        
                        x_c = x_bot_left + R
                        y_c = y_bot_left + R
                        # is it on the circle or somhere else inside the box ?
                        # if so we have a winner
                        if (x-x_c)**2 + (y-y_c)**2 < R**2:
                            return pos
                        # otherwise, because we are in the right box
                        # we can't be on another box so there is no hope 
                        # for finding a clicled marble
                        else:
                            return -1
                    else:
                        pos += 1
                    # then maybe it is on another box in the same row
                    # (the next iner loop iteration)
                # try on the next row
                else:
                    pos +=  self.theme['rows'][row]
                    break
        return -1

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
    main.init_window(random_pick=False, debug=True)
    #pyglet.clock.schedule_interval(main.update, 1)
    pyglet.app.run()