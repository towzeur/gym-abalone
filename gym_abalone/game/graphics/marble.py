import pyglet
from ..common.gameutils import AbaloneUtils

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
        r""" 
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