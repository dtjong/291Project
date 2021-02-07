import unittest
from .constraint_solver import *

class TestSolver(unittest.TestCase):
    def test_padding_no_frame_no_spacing(self):
        root = View((0, 0), (100, 100))
        child1 = View((10, 10), (90, 40), root)
        child2 = View((10, 60), (90, 90), root)

        child1.gen_padding(10)
        child2.gen_padding(10)

        view_list = [root, child1, child2]
        views_output = ConstraintSolver(view_list).constraint_to_coords()
        self.assertTrue(view_list = views_output)

if __name__ == '__main__':
    unittest.main()
