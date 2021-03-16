import unittest
from constraint_solver import *
from hierarchy import *

class TestHierarchyInference(unittest.TestCase):
    def test_hierarchy_inference_simple(self):
        root = View([0, 0], [100, 100])
        child1 = View([10, 10], [40, 90], root)
        child2 = View([60, 10], [90, 90], root)
        hierarchy = infer_hierarchy([root, child1, child2])
        self.assertListEqual(hierarchy.children, [child1, child2])

    def test_hierarchy_inference_two_levels(self):
        root = View([0, 0], [100, 100])
        child1 = View([10, 10], [40, 40], root)
        child2 = View([10, 60], [40, 90], root)
        child3 = View([60, 10], [90, 90], root)
        hierarchy = infer_hierarchy([root, child1, child2, child3])
        self.assertFalse(child1 in hierarchy.children)
        self.assertFalse(child2 in hierarchy.children)
        self.assertTrue(child3 in hierarchy.children)
        self.assertTrue(child1 in hierarchy.children[0].children)
        self.assertTrue(child2 in hierarchy.children[0].children)

class TestSolver(unittest.TestCase):
    def test_two_view_vstack(self):
        pass
        # root = View([15, 15], [52, 322], view_type=ViewType.HStack)
        # child1 = View([15, 15], [51, 50])
        # child2 = View([15, 62], [51, 307], view_mode=ViewMode.Unframed)
        # child3 = View([15, 362], [52, 322])

        # view_list = [root, child1, child2, child3]
        # views_output = ConstraintSolver(view_list).solve()

    def test_two(self):
        root = View([9.7, 8.5], [44.3, 364.75], view_type=ViewType.HStack)
        child1 = View([9.7, 8.5], [44.3, 43.75])
        child2 = View([9.7, 50.916666666666664], [44.3, 239.91666666666666], view_mode=ViewMode.Unframed)
        child3 = View([9.7, 247.08333333333331], [44.3, 282.3333333333333])
        child4 = View([9.7, 287.0833333333333], [44.3, 322.3333333333333])
        child5 = View([9.7, 329.5], [44.3, 364.75])

        view_list = [root, child1, child2, child3, child4, child5]
        views_output = ConstraintSolver(view_list).solve()

# Testing constraint -> coord math
class TestConstraints(unittest.TestCase):
    def test_padding_vstack(self):
        root = View([0, 0], [100, 100], view_type=ViewType.VStack)
        child1 = View([10, 10], [40, 90], root)
        child2 = View([60, 10], [90, 90], root)

        child1.gen_padding(10)
        child2.gen_padding(10)

        view_list = [root, child1, child2]
        views_output = ConstraintSolver(view_list).constraint_to_coords()
        self.assertListEqual(view_list, views_output)

    def test_padding_hstack(self):
        root = View([0, 0], [100, 100], view_type=ViewType.HStack)
        child1 = View([10, 10], [90, 40], root)
        child2 = View([10, 60], [90, 90], root)

        child1.gen_padding(10)
        child2.gen_padding(10)

        view_list = [root, child1, child2]
        views_output = ConstraintSolver(view_list).constraint_to_coords()
        self.assertListEqual(view_list, views_output)

    def test_frame_and_spacing(self):
        root = View([0, 0], [100, 100], view_type=ViewType.HStack)
        child1 = View([0, 0], [30, 30], root)
        child2 = View([0, 45], [50, 50], root)
        child3 = View([0, 65], [30, 90], root)

        root.gen_spacing(15)
        child1.gen_frame(30, 30)
        child2.gen_frame(50, 5)
        child3.gen_frame(30, 25)

        view_list = [root, child1, child2, child3]
        views_output = ConstraintSolver(view_list).constraint_to_coords()
        self.assertListEqual(view_list, views_output)

    def test_spacing(self):
        root = View([0, 0], [100, 100], view_type=ViewType.HStack)
        child1 = View([0, 0], [100, 20], root)
        child2 = View([0, 80], [100, 100], root)

        root.gen_spacing(60)

        view_list = [root, child1, child2]
        views_output = ConstraintSolver(view_list).constraint_to_coords()
        self.assertListEqual(view_list, views_output)


if __name__ == '__main__':
    unittest.main()
