import pyglet  
from ..common.gameutils import AbaloneUtils
from .marble import Marble

class Board:

    def __init__(self, game, theme, batch, groups, debug=False):

        self.game = game
        self.debug = debug

        self.theme = theme
        self.batch = batch
        self.groups = groups 

        # display the background
        im = AbaloneUtils.get_im_centered(self.theme['sprites']['board'], centered=False)
        self.sprite = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[0])

        self.marbles = None
        self.marbles_out = None

        self.current_pos = None

    def _delete_marbles_sprites(self):
        if self.marbles:
            for marble in self.marbles + self.marbles_out:
                if marble:
                    marble.delete()
                    del marble
            self.marbles     = None
            self.marbles_out = None

    def _reset_marbles_sprites(self):
        self.marbles = [None] * self.theme['locations']
        for player in range(self.game.players):
            for pos in self.game.players_sets[player]:
                marble = Marble(player, self.theme, self.batch, self.groups, debug=self.debug)
                marble.change_position(pos)
                self.marbles[pos] = marble
        self.marbles_out = []

    def reset(self):
        self._delete_marbles_sprites()
        self._reset_marbles_sprites()
        self.unset_current_pos()

    def unset_current_pos(self):
        if isinstance(self.current_pos, int) and self.marbles[self.current_pos]:
            self.marbles[self.current_pos].unselect()
        self.current_pos = None

    def set_current_pos(self, new_pos):
        # un select the previous selected posw
        self.unset_current_pos()
        
        # select the new one
        self.current_pos = new_pos
        self.marbles[new_pos].select()

    def update(self, modifications):
        if modifications is None:
            return

        # it's important to start with this because the prev_selec will change !
        self.unset_current_pos()
        for marble in self.marbles:
            if marble:
                marble.hide_arrow()

        for old_pos, new_pos, direction_index in modifications:
            if direction_index == -1: # eject
                self.marbles[old_pos].take_out(new_pos)
                self.marbles_out.append(self.marbles[old_pos])
                self.marbles[old_pos] = None
            else:
                # swap
                self.marbles[new_pos], self.marbles[old_pos] = self.marbles[old_pos], self.marbles[new_pos]
                # update sprites
                self.marbles[new_pos].change_position(new_pos)
                self.marbles[new_pos].change_direction(direction_index)
        
    def demo(self):
        import numpy as np
        for marble in self.marbles:
            if marble:
                # set random direction
                direction_index = np.random.randint(6)
                marble.change_direction(direction_index)

                # randomly select
                if np.random.rand() > .5:
                    marble.select()
