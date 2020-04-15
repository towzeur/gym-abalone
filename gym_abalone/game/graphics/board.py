import pyglet  
from ..common.gameutils import AbaloneUtils
from .marble import Marble

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
        import numpy as np
        for marble in self.marbles:
            if marble:
                # set random direction
                direction_index = np.random.randint(6)
                marble.change_direction(direction_index)

                # randomly select
                if np.random.rand() > .5:
                    marble.select()
