# standard libraries
import time

# third party libraries
import pyglet
from pyglet.window import key

from ..common.gameutils import AbaloneUtils
from ..engine.gamelogic import AbaloneGame
from .board import Board
from .header import Header


class AbaloneGui(pyglet.window.Window):
    def __init__(self, game, theme_name="default", debug=False):

        self.game = game
        self.theme_name = theme_name
        self.theme = AbaloneUtils.get_theme(theme_name)
        self.debug = debug

        # set the theme
        width = self.theme["dimension"]["width"]
        height = self.theme["dimension"]["height"] + self.theme["dimension"]["header_height"]

        # ============================== pyglet ===============================

        display = pyglet.canvas.get_display()
        screen = display.get_default_screen()
        # init the window's constructor
        super(AbaloneGui, self).__init__(screen=screen, width=width, height=height, vsync=False)

        self.set_caption("Gym Abalone")
        self.set_icon(AbaloneUtils.get_im_centered("assets/icons/icon_32x32.png", centered=False))

        self._center_window()
        # set the background color to white
        pyglet.gl.glClearColor(1, 1, 1, 1)
        # init the batch and group
        self.batch = pyglet.graphics.Batch()
        self.groups = [pyglet.graphics.OrderedGroup(i) for i in range(3)]

        # ============================== game component ==============================

        self.header = Header(self.game, self.theme, self.batch, self.groups)
        self.board = Board(self.game, self.theme, self.batch, self.groups, debug=self.debug)

        self.last_render = time.time()
        self.render_dt = 1

    def _center_window(self):
        # center the window
        x_centered = (self.screen.width - self.width) // 2
        y_centered = (self.screen.height - self.height) // 2
        self.set_location(x_centered, y_centered)

    def reset_game_gui(self, player=0, random_player=True, variant_name="classical", random_pick=False):
        self.game.reset(player=player, random_player=random_player, variant_name=variant_name, random_pick=random_pick)
        self.reset()

    def reset(self):
        # init the board
        self.board.reset()
        self.header.update()
        self.on_draw()

    def update(self, modifications, fps=None):
        # print(modifications)
        self.board.update(modifications)
        self.header.update()
        self.render(fps=fps)

    def action(self, pos):
        # if the player clicked on his own marble
        # set the focus to it

        pos_token = self.game.get_token_from_pos(pos)
        same_player = self.game.current_player == pos_token

        # no current pos
        if self.board.current_pos is None:
            if same_player:
                self.board.set_current_pos(pos)
                print("selected pos :", pos)

        # there is already a selected pos
        else:
            # change the current pos to another current player's marble
            if same_player:
                self.board.set_current_pos(pos)
                print("selected pos :", pos)
            # empty or another player
            else:
                move_check = self.game.action_handler(self.board.current_pos, pos, return_modif=True)
                if move_check:
                    move_type, modifications = move_check
                    self.update(modifications)
                    return move_type

    # =========================================================================
    #                              GYM INTEGRATION
    # =========================================================================

    def render(self, fps=None):
        # glClearColor(1,1,1,1)
        self.clear()
        self.batch.draw()
        self.switch_to()
        self.dispatch_events()
        self.flip()

        if fps:
            start = time.time()
            remaining = fps - (start - self.last_render)
            if remaining > 0:
                delta = 0
                while delta < remaining:
                    self.dispatch_events()
                    delta = time.time() - start
            self.last_render = time.time()

    # =========================================================================
    #                               PYGLET EVENTS
    # =========================================================================

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        # print(f'({x}, {y})')
        pos = AbaloneUtils.is_marbles_clicked(x, y, self.theme)
        if pos != -1:
            self.action(pos)

    def on_key_press(self, symbol, modifiers):
        pass
        """
        handlers = {
            key.LEFT  : (-1, 0),
            key.RIGHT : (+1, 0),
            key.DOWN  : (0, -1),
            key.UP    : (0, +1)
        }
        """
