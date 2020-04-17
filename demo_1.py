import pyglet
from pyglet import clock

import random
import time

from gym_abalone.game.graphics.abalonegui import AbaloneGui
from gym_abalone.game.engine.gamelogic import AbaloneGame

DT = 0.5

class Agents:

    @staticmethod
    def choice_random(game):
        
        player = game.current_player
        possible_moves = game.get_possible_moves(player, group_by_type=False)

        pos0, pos1 = random.choice(possible_moves)

        return pos0, pos1
    
    @staticmethod
    def choice_prioritize_random(game):
        
        player = game.current_player
        possible_moves = game.get_possible_moves(player, group_by_type=True)

        for move_type in ['ejected', 'inline_push', 'inline_move', 'sidestep_move']:
            if possible_moves[move_type]:
                pos0, pos1 = random.choice(possible_moves[move_type])
                break

        return pos0, pos1


def random_game(dt, gui):

    print(dt)

    t0 = time.time()
    #pos0, pos1 = Agents.choice_random(gui.game)
    pos0, pos1 = Agents.choice_prioritize_random(gui.game)
    print(pos0, pos1)
    # highlight the starting pos
    gui.action(pos0)
    
    # make a move
    def delayed_action(dt):
        move_type = gui.action(pos1)
        print(f"{gui.game.turns_count-1: <4} {move_type: >14}")
        if gui.game.game_over:
            print('NEW GAME')
            abalone_gui.reset_game_gui(random_pick=True)

    remaining = 0.5*DT - (time.time() - t0)
    pyglet.clock.schedule_once(delayed_action, max(0,  remaining))

    

if __name__ == '__main__':

    game = AbaloneGame()
 
    abalone_gui = AbaloneGui(game)
    abalone_gui.reset_game_gui(variant_name='anglattack', random_pick=False)

    
    pyglet.clock.schedule_interval(random_game, DT, abalone_gui)

    pyglet.app.run()
    print('good bye !')

