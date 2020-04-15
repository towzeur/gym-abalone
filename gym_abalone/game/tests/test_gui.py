import random
import unittest
import math

from main import window

class TestGoEnv(unittest.TestCase):

    def test_click(self):

        gui = window()
        gui.init_window(variant_name='classical', random_pick=False, debug=True)

        R = gui.theme['dimension']['marble_radius']
        pos = 0
        for pos, (x_bot_left, y_bot_left) in enumerate(gui.theme['coordinates']):
            # get the center of the circle
            x_c = x_bot_left + R
            y_c = y_bot_left + R
            # add some noise 
            noise_x = R * random.random()
            noise_y = (R - noise_x) * random.random()
            x = x_c + noise_x
            y = y_c + noise_y
            #
            pos_computed = gui.is_marbles_clicked(x, y)
            self.assertEqual(pos, pos_computed)

if __name__ == '__main__':
    unittest.main()


