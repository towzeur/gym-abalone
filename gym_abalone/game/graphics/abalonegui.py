import pyglet
from pyglet.window import key
from ..engine.gamelogic import AbaloneGame
from ..common.gameutils import AbaloneUtils
from .board import Board
from .header import Header

class AbaloneGui(pyglet.window.Window):

    def __init__(self, theme="default"):

        # set the theme 
        self.theme = AbaloneUtils.get_theme(theme) 
        width  = self.theme['dimension']['width']
        height = self.theme['dimension']['height'] + self.theme['dimension']['header_height']            

        # ============================== pyglet ===============================

        display = pyglet.canvas.get_display()
        screen = display.get_default_screen()
        # init the window's constructor
        super(AbaloneGui, self).__init__(screen=screen, width=width, height=height, vsync=False)
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
        pass
        '''
        handlers = {
            key.LEFT  : (-1, 0),
            key.RIGHT : (+1, 0),
            key.DOWN  : (0, -1),
            key.UP    : (0, +1)
        }
        '''