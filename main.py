import pyglet
import numpy as np


class window(pyglet.window.Window):

    def __init__(self, width=1100, height=750):

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
        self.bgs = []


    def on_draw(self):
        self.clear()
        self.batch.draw()

    def start(self):
        pass

    def update(self, dt):
        pass


if __name__ == '__main__':
    
    main = window(width=800, height=800)
    main.start()

    pyglet.clock.schedule_interval(main.update, 1 / 60)
    pyglet.app.run()