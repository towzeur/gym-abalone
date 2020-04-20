import random
import unittest
import math

from main import window

class TestGoEnv(unittest.TestCase):

    def test_inlinepush(self):

        gui = window()
        gui.init_window(variant_name='classical', random_pick=False, debug=True)

        self.assertEqual(pos, pos_computed)

if __name__ == '__main__':
    unittest.main()


