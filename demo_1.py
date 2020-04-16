import pyglet
from gym_abalone.game.graphics.abalonegui import AbaloneGui


if __name__ == '__main__':
    
    abalone_gui = AbaloneGui()
    abalone_gui.start(variant_name='anglattack', random_pick=False, debug=True)
    #abalone_gui.start(random_pick=True, debug=False)
    #pyglet.clock.schedule_interval(abalone_gui.update, 1)
    pyglet.app.run()

    print('hello')

