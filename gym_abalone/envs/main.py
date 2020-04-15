import pyglet
from pyglet.window import key
import numpy as np
from pprint import pprint
import time
import json

from gamelogic import AbaloneGame
from gameutils import AbaloneUtils


class Marble:
    
    DEBUG_STYLE = {
        'font_name' : 'Arial', 
        'font_size' : 24,
        'anchor_x'  : 'center', 
        'anchor_y'  : 'center'
    }

    LABEL_COLORS = {
        'default' : (0, 0, 0, 255),
        0  : (0, 0, 0, 255),
        1  : (255, 255, 255, 255)
    }
    
    def __init__(self, player, theme, batch, groups, debug=False):
        self.player = player

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
            color = Marble.LABEL_COLORS.get(self.player, Marble.LABEL_COLORS['default'])
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
                self.sprites['label'].draw()
            
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

    def hide_arrow(self):
        self.sprites['arrow'].visible = False
    
    def select(self):
        self.sprites['selected'].visible = True

    def unselect(self):
        self.sprites['selected'].visible = False

    def take_out(self, out_index):
        if out_index < len(self.theme['out_coordinates'][self.player]):
            x_out, y_out = self.theme['out_coordinates'][self.player][out_index]
            self.sprites['marble'].update(x=x_out, y=y_out)

            self.sprites['arrow'].visible = False
            self.sprites['selected'].visible = False

            if self.debug:
                self.sprites['label'].x = x_out
                self.sprites['label'].y = y_out
                self.sprites['label'].text = f'.{out_index}'
                self.sprites['label'].visible = False

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

    def _init_sprites(self):
        self.infos_sprites = []
        for _ in range(len(Header.DISPLAYED_INFO)):
            info = pyglet.text.Label(batch=self.batch, group=self.groups[1], **Header.INFO_STYLE)
            self.infos_sprites.append(info)

    def draw(self, infos_tuple):
        #assert len(Header.DISPLAYED_INFO) == len(infos_tuple)
        x =  0
        y = self.y0 + self.height // 2

        for i, (info_name, info_data) in enumerate(zip(Header.DISPLAYED_INFO, infos_tuple)):
            x += Header.PADDING_X

            displayed_string = f"{info_name} : {info_data}"

            self.infos_sprites[i].text = displayed_string
            self.infos_sprites[i].x = x 
            self.infos_sprites[i].y = y

            x += self.infos_sprites[i].content_width

    def get_infos_tuple(self, game):
        infos_tuple = [None] * len(Header.DISPLAYED_INFO)
        infos_tuple[0] = self.theme["players_name"][game.current_player]
        infos_tuple[1] = 0 #"episode",
        infos_tuple[2] = game.turns_count
        infos_tuple[3] = 0 #"elapsed time",
        infos_tuple[4] = 'TODO' # '"game state"
        return infos_tuple

    def update(self, game):
        infos_tuple = self.get_infos_tuple(game)
        self.draw(infos_tuple)
    
class Board:

    def __init__(self, theme, batch, groups):
        self.theme = theme
        self.batch = batch
        self.groups = groups 

        # display the background
        im = AbaloneUtils.get_im_centered(self.theme['sprites']['board'], centered=False)
        self.sprite = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[0])

        self.marbles = None
        self.marbles_out = None

    def _reset_marbles(self):
        # reset players's sprites
        if self.marbles:
            for marble in self.marbles + self.marbles_out:
                if marble:
                    marble.delete()
                    del marble
            self.marbles = None
            self.marbles_out = None

    def _init_marbles(self, game, debug=False):
        # init marbles
        self.marbles = [None] * self.theme['locations']
        for player in range(game.players):
            for pos in game.players_sets[player]:
                marble = Marble(player, self.theme, self.batch, self.groups, debug=debug)
                marble.change_position(pos)
                self.marbles[pos] = marble
        self.marbles_out = []


    def init_board(self, game, debug=False):
        self._reset_marbles()
        self._init_marbles(game, debug=debug)


    def update(self, modifications):
        if modifications is None:
            return

        # it's important to start with this becayse the prev_selec will change !
        if 'new_turn' in modifications:
            self.marbles[modifications['new_turn']].unselect()
            for marble in self.marbles:
                if marble:
                    marble.hide_arrow()

        # change selected marble
        if 'selected' in modifications:
            old_pos, new_pos = modifications['selected']
            if old_pos is not None and self.marbles[old_pos] is not None:
                self.marbles[old_pos].unselect()
            self.marbles[new_pos].select()

        if 'damage' in modifications:
            old_pos, out_index = modifications['damage']
            self.marbles[old_pos].take_out(out_index)
            self.marbles_out.append(self.marbles[old_pos])
            self.marbles[old_pos] = None
        
        if 'moves' in modifications:
            for old_pos, new_pos, angle in modifications['moves']:
                # swap
                self.marbles[new_pos], self.marbles[old_pos] = self.marbles[old_pos], self.marbles[new_pos]
                # update sprites
                self.marbles[new_pos].change_position(new_pos)
                self.marbles[new_pos].change_direction(angle)

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

    def start(self, player=0, random_player=True, variant_name='classical', random_pick=True, debug=False):
        # init the game
        self.game.init_game(
            player=player, random_player=True,
            variant_name=variant_name, random_pick=random_pick
        )
        # init the board
        self.board.init_board(self.game, debug=debug)
        self.header.update(self.game)

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def update(self, dt):
        # set random variant
        self.start(random_pick=True, debug=False)
        self.board.demo()

    def on_mouse_press(self, x, y, button, modifiers):
        #print(f'({x}, {y})')
        pos = AbaloneUtils.is_marbles_clicked(x, y, self.theme)
        if pos != -1:
            modifications = self.game.action_handler(pos)
            #print(modifications)
            self.board.update(modifications)
            self.header.update(self.game)

    def on_key_press(self, symbol, modifiers):
        handlers = {
            key.LEFT  : (-1, 0),
            key.RIGHT : (+1, 0),
            key.DOWN  : (0, -1),
            key.UP    : (0, +1)
        }


if __name__ == '__main__':

    abalone_gui = window()
    #abalone_gui.start(variant_name='anglattack', random_pick=False, debug=True)
    abalone_gui.start(random_pick=True, debug=False)
    #pyglet.clock.schedule_interval(abalone_gui.update, 1)
    pyglet.app.run()