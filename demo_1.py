import pyglet
from pyglet import clock
from gym_abalone.game.graphics.abalonegui import AbaloneGui
import random
import time

DT = 1

def random_game(dt, gui):

    t0 = time.time()
    game = gui.game
    player = game.current_player

    possible_moves = game.get_possible_moves(player)
    for move_type in ['ejected', 'inline_push', 'sidestep_move', 'inline_move']:
        if possible_moves[move_type]:
            pos0, pos1 = random.choice(possible_moves[move_type])
            break
    
    # highlight the selected move
    gui.action(pos0)
    gui.on_draw()
    
    # make a move
    remaining = 0.9*DT - (time.time() - t0)
    if remaining > 0:
        pyglet.clock.schedule_once(lambda dt, g, p1 : g.action(p1) , remaining, abalone_gui, pos1)
    else:
        gui.action(pos1)

    if game.game_over:
        abalone_gui.start(random_pick=True, debug=False)
    print()



if __name__ == '__main__':
    
    abalone_gui = AbaloneGui()
    abalone_gui.start(variant_name='anglattack', random_pick=False, debug=False)
    #abalone_gui.start(random_pick=True, debug=False)
    pyglet.clock.schedule_interval(random_game, 1, abalone_gui)
    pyglet.app.run()
    print('good bye !')

