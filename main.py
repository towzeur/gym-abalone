import pyglet
from pyglet.window import key
import numpy as np
from pprint import pprint
import time
import json

from gamelogic import AbaloneGame
from gameutils import AbaloneUtils


class Marble:
    
    LABEL_COLORS = {
        'default' : (0, 0, 0, 255),
        1  : (0, 0, 0, 255),
        2  : (255, 255, 255, 255)
    }
    
    def __init__(self, player, theme, batch, groups, debug=True):
        self.player = player
        self.player_token = player + 1

        self.theme = theme
        self.batch = batch
        self.groups = groups
        self.debug = debug

        self.sprite = None
        self.label = None
        self._init_sprites()

        self.pos = None

    def _init_sprites(self):
        # marble sprite
        im_path = self.theme['sprites']['players'][self.player]
        im = pyglet.image.load(im_path)
        self.sprite = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[1])
        # label sprite if debug
        if self.debug:
            color = Marble.LABEL_COLORS.get(self.player_token, Marble.LABEL_COLORS['default'])
            self.label = pyglet.text.Label(
                font_name='Roboto', font_size=28,
                color = color,
                anchor_x='center', anchor_y='center',
                batch=self.batch, group=self.groups[2]
            )

    def delete(self):
        if self.sprite:
            self.sprite.delete()
            self.sprite = None
        if self.label:
            self.label.delete()
            self.label = None

    def change_position(self, pos):
        if self.pos != pos:
            self.pos = pos

            x_new, y_new = self.theme['coordinates'][pos]
            self.sprite.update(x_new, y_new)

            if self.debug:
                self.label.x = x_new + self.theme['dimension']['marble_radius']
                self.label.y = y_new + self.theme['dimension']['marble_radius']
                self.label.text = str(pos)


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
        
        # selected sprite
        selected_sprite = pyglet.image.load(self.theme['sprites']['selected'])
        self.selected_sprite = pyglet.sprite.Sprite(selected_sprite, batch=self.batch, group=self.groups[2])
        self.selected_sprite.visible = False

        self.marbles = None

    def init_window(self, variant_name='classical', random_pick=True, debug=True):
        # reset the game
        self.game.init_game(variant_name=variant_name, random_pick=random_pick)

        # reset players's sprites
        if self.marbles:
            for marble in self.marbles:
                if marble:
                    marble.delete()
                    del marble

        # init marbles
        self.marbles = [None] * self.theme['locations']
        for player in range(self.game.players):
            for pos in self.game.players_sets[player]:
                marble = Marble(player, self.theme, self.batch, self.groups, debug=debug)
                marble.change_position(pos)
                self.marbles[pos] = marble

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def update(self, dt):
        self.init_window(random_pick=True, debug=True)


    def on_mouse_press(self, x, y, button, modifiers):
        print(f'({x}, {y})')
        pos = self.is_marbles_clicked(x, y)

        if pos != -1:

            token = self.game.action(pos)
           
            if token != self.game.TOKEN_EMPTY:

                # show the slected border
                x, y = self.theme['coordinates'][pos]
                offset = (self.selected_sprite.width - 48)/2
                self.selected_sprite.visible = True
                self.selected_sprite.update(x=x-offset, y=y-offset)

                #player = token - 1
                # find the cell
                #for cell in self.players_cells[player]:
                #    if cell['pos'] == pos:
                #        pass
                        
                '''
                damage_index = self.game.players_damages[player]
                new_x, new_y = self.theme['out_coordinates'][player][damage_index]
                cell['sprite'].update(x=new_x, y=new_y)
                # increase damage
                self.game.players_damages[player] += 1
                break
                '''
                    

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
                # are we in the good row ?
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
                        # otherwise, because the click is within in the right box
                        # it can't be on another box
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