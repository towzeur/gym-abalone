import pyglet
from pyglet.window import key
import numpy as np
from pprint import pprint
import time
import json

class window(pyglet.window.Window):

    def __init__(self, theme="default"):

        # get the theme
        self.theme = self.get_theme(theme)
        width  = self.theme['dimension']['width']
        height = self.theme['dimension']['height']

        display = pyglet.canvas.get_display()
        screen = display.get_default_screen()

        screen_width = screen.width
        screen_height = screen.height

        # init the window
        super(window, self).__init__(screen=screen, width=width, height=height, vsync=False)

        # center the window
        x_centered = (screen_width - self.width) // 2
        y_centered = (screen_height - self.height) // 2
        self.set_location(x_centered, y_centered)

        # set the background color to white
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.batch = pyglet.graphics.Batch()

        # create layers
        self.groups = [pyglet.graphics.OrderedGroup(i) for i in range(self.theme['locations']+1)]

        # display the background 
        board_image = pyglet.image.load(self.theme['sprites']['board'])
        self.board_sprite = pyglet.sprite.Sprite(board_image, batch=self.batch, group=self.groups[0])
        
        self.locations = [None] * self.theme['locations']
    
    @staticmethod
    def get_theme(theme_name):
        with open('asset/themes.json', 'r') as f:
            themes = json.load(f)
        if theme_name in themes:
            return themes[theme_name]
        return themes['default']

    def on_draw(self):
        self.clear()
        self.batch.draw()

    def start(self):
        player = 1
        for pos in range(self.theme['locations']):
            self.place_box(pos, player=player)
            # player : 1->2 and 2->1
            player = 3-player
                
    def place_box(self, pos, player=1):
        im_path = self.theme['sprites'][f'player_{player}']
        im = pyglet.image.load(im_path)

        x, y = self.theme['coordinates'][pos]

        sprite = pyglet.sprite.Sprite(im, batch=self.batch, group=self.groups[pos+1], x=x, y=y)
        self.locations[pos] = sprite

    def update(self, dt):
        return 

    def on_mouse_press(self, x, y, button, modifiers):
        print(x, y)
    
    def on_key_press(self, symbol, modifiers):
        
        tmp = {
            key.LEFT  : (-1, 0),
            key.RIGHT : (+1, 0),
            key.DOWN  : (0, -1),
            key.UP    : (0, +1)
        }

        i = 1

        if symbol in tmp:
            x, y = self.locations[i].position
            dx, dy = tmp[symbol]
            new_x, new_y = x+dx, y+dy
            self.locations[i].update(x=new_x, y=new_y)
            print(new_x, new_y)



if __name__ == '__main__':

    main = window()
    main.start()

    #pyglet.clock.schedule_interval(main.update, 1 / 60)
    pyglet.app.run()