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

        self.sprites = { sprite_name : None for sprite_name in
            ['marble', 'label', 'arrow', 'selected']
        }
        self._init_sprites()

        self.pos = None

    def _init_sprites(self):
        # marble sprite
        im = AbaloneUtils.get_im_centered(self.theme['sprites']['players'][self.player])
        self.sprites['marble'] = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[1])

        # label sprite if debug
        if self.debug:
            color = Marble.LABEL_COLORS.get(self.player_token, Marble.LABEL_COLORS['default'])
            self.sprites['label']  = pyglet.text.Label(
                font_name='Roboto', font_size=28,
                color = color,
                anchor_x='center', anchor_y='center',
                batch=self.batch, group=self.groups[2]
            )
        
        # direction arrow sprite
        im = AbaloneUtils.get_im_centered(self.theme['sprites']['arrows'][self.player])
        self.sprites['arrow'] = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[2])
        self.sprites['arrow'].visible = False

        # selected sprite
        im = AbaloneUtils.get_im_centered(self.theme['sprites']['selected'])
        self.sprites['selected'] = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[2])
        self.sprites['selected'].visible = False


    def delete(self):
        for sprite_name, sprite in self.sprites.items(): 
            if sprite:
                sprite.delete()
                del self.sprites[sprite_name]
                self.sprites[sprite_name] = None

    def change_position(self, pos):
        if self.pos != pos:
            self.pos = pos

            x_new, y_new = self.theme['coordinates'][pos]
            self.sprites['marble'].update(x_new, y_new)
            self.sprites['arrow'].update(x_new, y_new)
            self.sprites['selected'].update(x_new, y_new)

            if self.debug:
                self.sprites['label'].x = x_new
                self.sprites['label'].y = y_new
                self.sprites['label'].text = str(pos)
            

    
    def change_direction(self, direction_index):
        """ change the arrow angle to show up a new direction

        Args:
            direction_index (int): the direction index 0<=  <6
                ie : 
                           4     5
                            \   /
                             \ /
                      3 ----- * ----- 0 
                             /  \
                            /    \ 
                           2      1
        """
        angle = direction_index * 60 #(360 / 6)
        self.sprites['arrow'].update(rotation=angle)
        self.sprites['arrow'].visible = True
    
    def select(self):
        self.sprites['selected'].visible = True

    def unselect(self):
        self.sprites['selected'].visible = False

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
        selected_im = pyglet.image.load(self.theme['sprites']['selected'])
        selected_im.anchor_x = selected_im.width  // 2
        selected_im.anchor_y = selected_im.height // 2
        self.selected_sprite = pyglet.sprite.Sprite(selected_im, batch=self.batch, group=self.groups[2])
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
        # set random variant
        self.init_window(random_pick=True, debug=False)

        for marble in self.marbles:
            if marble:
                # set random direction
                direction_index = np.random.randint(6)
                marble.change_direction(direction_index)

                # randomly select
                if np.random.rand() > .5:
                    marble.select()

    def on_mouse_press(self, x, y, button, modifiers):
        print(f'({x}, {y})')

        pos = AbaloneUtils.is_marbles_clicked(x, y, self.theme)
        if pos != -1:
            token = self.game.action(pos)
            if token != self.game.TOKEN_EMPTY:

                # show the slected border
                self.mables[pos].select() 

                #x, y = self.theme['coordinates'][pos]

                #player = token - 1
                # find the cell
                #for cell in self.players_cells[player]:
                #    if cell['pos'] == pos:
                #        pass
                    
                #damage_index = self.game.players_damages[player]
                #new_x, new_y = self.theme['out_coordinates'][player][damage_index]
                #cell['sprite'].update(x=new_x, y=new_y)
                # increase damage
                #self.game.players_damages[player] += 1
                #break

    def on_key_press(self, symbol, modifiers):
        
        tmp = {
            key.LEFT  : (-1, 0),
            key.RIGHT : (+1, 0),
            key.DOWN  : (0, -1),
            key.UP    : (0, +1)
        }

        if symbol in tmp:
            pass
            #self.init_window()
            
            #x, y = self.locations[i].position
            #dx, dy = tmp[symbol]
            #new_x, new_y = x+dx, y+dy
            #self.locations[i].update(x=new_x, y=new_y)
            #print(new_x, new_y)
        
            #for marble in self.marbles:
            #    if marble:
            #        direction_index = np.random.randint(6)
            #        marble.change_direction(direction_index)


if __name__ == '__main__':

    abalone_gui = window()
    abalone_gui.init_window(random_pick=False, debug=True)
    pyglet.clock.schedule_interval(abalone_gui.update, 1)
    pyglet.app.run()