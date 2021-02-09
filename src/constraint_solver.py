from z3 import *
from enum import IntEnum

class ViewType(IntEnum):
    VStack = 0
    HStack = 1
    Leaf = 2

class View:
    def __init__(self, top_left, bot_right, parent=None, view_type=ViewType.Leaf):
        self.top_left = top_left
        self.bot_right = bot_right
        self.parent = parent
        self.view_type = view_type

        # Constraints for H/VStack
        self.spacing_constraint = 0
        # Constraints for leaf views
        self.padding_constraint = [[0, 0], [0, 0]]
        self.frame_constraint = None

    def __eq__(self, other):
        return self.top_left == other.top_left and self.bot_right == other.bot_right

    def __str__(self):
        return str(self.top_left) + ", " + str(self.bot_right)

    # 0 for height, 1 for width
    def size(self, axis):
        return self.bot_right[axis] - self.top_left[axis]

    def is_framed(self, axis):
        return self.frame_constraint != None and self.frame_constraint[axis] != None

    # Below are functions to generate the constraints
    def gen_padding(self, top, bot=None, left=None, right=None):
        if bot == None:
            bot = top
        if left == None:
            left = top
        if right == None:
            right = left
        self.padding_constraint = [[top, bot], [left, right]]
    def gen_spacing(self, spacing):
        self.spacing_constraint = spacing

    def gen_frame(self, height=None, width=None):
        self.frame_constraint = [height, width]

# Constraint Solver for one level (no hierarchy)
class ConstraintSolver:
    def __init__(self, views):
        self.s = Solver()
        self.views = views

    def verify(self):
        constrained_views = self.constraint_to_coords()
        return constrained_views == self.views

    # Outputs a list of views in the same format as the input
    def constraint_to_coords(self):
        if len(self.views) == 0:
            return
        root = self.views[0]
        major_axis = int(root.view_type)
        minor_axis = int(ViewType.HStack if root.view_type == ViewType.VStack else ViewType.VStack)
        children = self.views[1:]
        # Calculating width/height of frameless views
        spacing = (len(children) - 1) * root.spacing_constraint
        framed = filter(lambda view: view.is_framed(major_axis), children)
        num_frameless = len(list(filter(lambda view: not view.is_framed(major_axis), children)))
        pad_sum = sum([sum(view.padding_constraint[major_axis])
                       for view in children])
        framed_sum = sum([view.frame_constraint[major_axis]
                          for view in framed])
        size = root.size(major_axis) # size along major axis
        fsize = (size - spacing - pad_sum - framed_sum) / num_frameless if num_frameless > 0 else 0
        if fsize < 0:
            return
        last = 0
        result = [root]
        for view in children:
            top_left = root.top_left.copy()
            last += view.padding_constraint[major_axis][0]
            top_left[major_axis] += last
            top_left[minor_axis] += view.padding_constraint[minor_axis][0]
            bot_right = top_left.copy()
            if view.is_framed(major_axis):
                bot_right[major_axis] += view.frame_constraint[major_axis]
            else:
                bot_right[major_axis] += fsize
            last = bot_right[major_axis] + view.padding_constraint[major_axis][1] + root.spacing_constraint

            if view.is_framed(minor_axis):
                bot_right[minor_axis] += view.frame_constraint[minor_axis]
            else:
                bot_right[minor_axis] = root.bot_right[minor_axis] - view.padding_constraint[minor_axis][1]
            result.append(View(top_left, bot_right))
        return result
