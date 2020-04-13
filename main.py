import pyglet
from pyglet.window import key
import numpy as np
from pprint import pprint
import time
import json

from gamelogic import AbaloneGame
from gameutils import AbaloneUtils, debug


class Marble:
    
    DEBUG_STYLE = {
        'font_name' : 'Arial', 
        'font_size' : 24,
        'anchor_x'  : 'center', 
        'anchor_y'  : 'center'
    }

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
            self.sprites['label'] = pyglet.text.Label(
                color=color,
                batch=self.batch, group=self.groups[2],
                **Marble.DEBUG_STYLE
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
        """ 
        change the arrow's sprite angle to match a new direction

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

    def take_out(self, out_index):
        if out_index<len(self.theme['out_coordinates'][self.player]):
            x_out, y_out = self.theme['out_coordinates'][self.player][out_index]
            self.sprites['marble'].update(x=x_out, y=y_out)
            self.sprites['arrow'].visible = False
            self.sprites['selected'].visible = True


class Header:

    DISPLAYED_INFO = [
        "player turn",
        "episode",
        "turns",
        "elapsed time",
        "game state"
    ]

    
    DISPLAYED_INFO_DEFAULT_DATA = [
        "0",
        "0",
        "1",
        "0",
        "WAITING"
    ]

    INFO_STYLE = {
        'font_name' : 'Arial',
        'font_size' : 12,
        'bold'      : True,
        'color'     : (255, 255, 255, 255),
        'anchor_x'  : 'left', 
        'anchor_y'  : 'center',
    }

    PADDING_X = 30 # pixel

    def __init__(self, theme, batch, groups):
        self.theme = theme
        self.batch = batch
        self.groups = groups

        self.x0, self.y0 = 0, self.theme['dimension']['height']

        # display header background sprite
        im = AbaloneUtils.get_im_centered(self.theme['sprites']['header'], centered=False)
        sprite = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[0], x=self.x0, y=self.y0)
        self.header_sprite = sprite
        self.width, self.height = sprite.width, sprite.height

        self.infos_sprites = None
        self._init_sprites()

        self.draw(Header.DISPLAYED_INFO_DEFAULT_DATA)

    def _init_sprites(self):
        self.infos_sprites = []
        for _ in range(len(Header.DISPLAYED_INFO)):
            info = pyglet.text.Label(batch=self.batch, group=self.groups[1], **Header.INFO_STYLE)
            self.infos_sprites.append(info)

    @debug
    def draw(self, infos_tuple):
        assert len(Header.DISPLAYED_INFO) == len(infos_tuple)

        x =  0
        y = self.y0 + self.height // 2

        for i, (info_name, info_data) in enumerate(zip(Header.DISPLAYED_INFO, infos_tuple)):
            x += Header.PADDING_X

            displayed_string = f"{info_name} : {info_data}"

            self.infos_sprites[i].text = displayed_string
            self.infos_sprites[i].x = x 
            self.infos_sprites[i].y = y

            x += self.infos_sprites[i].content_width
    

class Board:

    def __init__(self, theme, batch, groups):
        self.theme = theme
        self.batch = batch
        self.groups = groups 

        # display the background
        im = AbaloneUtils.get_im_centered(self.theme['sprites']['board'], centered=False)
        self.sprite = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[0])

        self.marbles = None
        self.current_selected_pos = None


    def _reset_marbles(self):
        # reset players's sprites
        if self.marbles:
            for marble in self.marbles:
                if marble:
                    marble.delete()
                    del marble
            self.marbles = None

    def _init_marbles(self, game, debug=True):
        # init marbles
        self.marbles = [None] * self.theme['locations']
        for player in range(game.players):
            for pos in game.players_sets[player]:
                marble = Marble(player, self.theme, self.batch, self.groups, debug=debug)
                marble.change_position(pos)
                self.marbles[pos] = marble

    def init_board(self, game, debug=debug):
        self._reset_marbles()
        self._init_marbles(game)
        self.current_selected = None
    
    def change_current_selected(self, pos):
        marble = self.marbles[pos]
        # if the cell is occupied

        if marble:
            if self.current_selected_pos is not None:
                self.marbles[self.current_selected_pos].unselect()
            marble.select()
            self.current_selected_pos = pos

        elif self.current_selected_pos is not None:
            # update the current pos
            old_pos = self.current_selected_pos
            self.current_selected_pos = pos

            # change the marble's position
            self.marbles[old_pos].change_position(pos)

            # update the list
            self.marbles[pos], self.marbles[old_pos] = self.marbles[old_pos], self.marbles[pos]

            
    def demo(self):
        for marble in self.marbles:
            if marble:
                # set random direction
                direction_index = np.random.randint(6)
                marble.change_direction(direction_index)

                # randomly select
                if np.random.rand() > .5:
                    marble.select()


class window(pyglet.window.Window):

    def __init__(self, theme="default"):

        # set the theme 
        self.theme = AbaloneUtils.get_theme(theme) 
        width  = self.theme['dimension']['width']
        height = self.theme['dimension']['height'] + self.theme['dimension']['header_height']            

        # ============================== pyglet ===============================

        display = pyglet.canvas.get_display()
        screen = display.get_default_screen()
        # init the window's constructor
        super(window, self).__init__(screen=screen, width=width, height=height, vsync=False)
        self._center_window()
        # set the background color to white
        pyglet.gl.glClearColor(1, 1, 1, 1)
        # init the batch and group
        self.batch = pyglet.graphics.Batch()
        self.groups = [pyglet.graphics.OrderedGroup(i) for i in range(3)]

        # ============================== game component ==============================

        self.game = AbaloneGame() # game engine
        self.header = Header(self.theme, self.batch, self.groups)
        self.board = Board(self.theme, self.batch, self.groups)

    def _center_window(self):
        # center the window
        x_centered = (self.screen.width - self.width) // 2
        y_centered = (self.screen.height - self.height) // 2
        self.set_location(x_centered, y_centered)

    def init_window(self, variant_name='classical', random_pick=True, debug=True):
        # init the game
        self.game.init_game(variant_name=variant_name, random_pick=random_pick)
        # init the board
        self.board.init_board(self.game, debug=debug)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def update(self, dt):
        # set random variant
        self.init_window(random_pick=True, debug=False)

        self.board.demo()

    @debug
    def on_mouse_press(self, x, y, button, modifiers):
        print(f'({x}, {y})')

        pos = AbaloneUtils.is_marbles_clicked(x, y, self.theme)

        if pos != -1:
            self.board.change_current_selected(pos)

            # damage it
            #damage_index = self.game.players_damages[marble.player]
            #marble.take_out(damage_index)
            #game.players_damages[marble.player] += 1
                    

    def on_key_press(self, symbol, modifiers):
        
        tmp = {
            key.LEFT  : (-1, 0),
            key.RIGHT : (+1, 0),
            key.DOWN  : (0, -1),
            key.UP    : (0, +1)
        }

        infos_tuple = [0] * len(Header.DISPLAYED_INFO)
        self.header.draw(infos_tuple)

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
    #pyglet.clock.schedule_interval(abalone_gui.update, 1)
    pyglet.app.run()