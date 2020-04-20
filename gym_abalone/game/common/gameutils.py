import json
import random
import pyglet
import os
from pathlib import Path

class AbaloneUtils:

    @staticmethod
    def load_fonts(dirname='assets/fonts/'):
        path = Path(os.path.dirname(os.path.realpath(__file__))).parent
        path = path.joinpath(dirname)
        for font_filename in os.listdir(path):
            filename = str(path.joinpath(font_filename))
            print(filename)
            pyglet.font.add_file(filename)

    @staticmethod
    def _safe_json_pick(target, filename, default, random_pick):

        path = Path(os.path.dirname(os.path.realpath(__file__))).parent
        path =  path.joinpath(filename)
  
        with open(path, 'r') as f:
            options = json.load(f)
        if random_pick:
            return random.choice(list(options.values()))
        if target in options:
            return options[target]
        return options[default]

    @staticmethod
    def get_theme(theme_name='default', random_pick=False):
        return AbaloneUtils._safe_json_pick(theme_name, 'assets/themes.json', 'default', random_pick)
    
    @staticmethod
    def get_variants(variant_name='classical', random_pick=False):
        return AbaloneUtils._safe_json_pick(variant_name, 'assets/variants.json', 'classical', random_pick)
    
    @staticmethod
    def get_im_centered(im_path, centered=True):

        # resolve path
        path = Path(os.path.dirname(os.path.realpath(__file__))).parent
        path =  path.joinpath(im_path)
        
        im = pyglet.image.load(path)
        if centered:
            im.anchor_x = im.width  // 2
            im.anchor_y = im.height // 2
        return im

    @staticmethod
    def is_marbles_clicked(x, y, theme):
        """
        return the pos of the clicked marble for a given theme.
        
        It do so by starting in the first row and increse the col.
        It's a bit better than bruteforce because it skips the current row if the 
        first elt (first column) is not within the outter box.
        if the click is find inside a box, it compute the L2 norm to find
        if the click is inded upon the marble.

        Returns:
            (int) pos : pos of the clicked marble if it exists (0 < pos < self.theme['locations'] )
            (int)  -1 : otherwise
        """

        R = theme['dimension']['marble_radius']

        pos = 0
        for row, nb_col in enumerate(theme['rows']):
            for col in range(nb_col):
                x_c, y_c = theme['coordinates'][pos]
                # we first start by checking if the click is in the circle's outter box
                # are we in the good row ?
                if abs(y -  y_c) <= R:
                    # then if a solution exist it may be on this row
                    # is it on this box ?
                    if abs(x -  x_c) <= R:
                        # is it on the circle or somwhere else inside the box ?
                        # if so we have a winner
                        if (x-x_c)**2 + (y-y_c)**2 < R**2:
                            return pos
                        # otherwise, because the click is within in the right box
                        # it can't be on another box
                        else:
                            return -1
                    else:
                        pos += 1
                    # then maybe it is on another box in the same row
                    # (the next iner loop iteration)
                # try on the next row
                else:
                    pos +=  theme['rows'][row]
                    break
        return -1

    @staticmethod
    def debug(f):
        def f_wrapped(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except Exception as e:
                print(e)
        return f_wrapped
