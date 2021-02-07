from z3 import *
from enum import Enum

class ViewType(Enum):
    VStack = 1
    HStack = 2
    Leaf = 3

class View:
    def __init__(self, top_left, bot_right, parent=None, view_type=ViewType.Leaf):
        self.top_left = top_left
        self.bot_right = bot_right
        self.parent = parent

        # Constraints for H/VStack
        self.spacing_constraint = 0
        # Constraints for leaf views
        self.padding_constraint = None
        self.frame_constraint = None

    def __eq__(self, other):
        return self.top_left == other.top_left and self.bot_right == other.bot_right

    # 0 for width, 1 for height
    def size(self, axis):
        return bot_right[axis] - top_left[axis]

    # Below are functions to generate the constraints
    def gen_padding(self, top, bot=None, left=None, right=None):
        if bot == None:
            bot = top
        if left == None:
            left = top
        if right == None:
            right = left
        self.padding_constraint = {
            "top": top,
            "bot": bot,
            "left": left,
            "right": top,
        }

    def gen_spacing(self, spacing):
        self.spacing_constraint = spacing

    def gen_frame(self, width=None, height=None):
        self.frame_constraint = {
            "width": width,
            "height": height
        }

class ConstraintSolver:
    def __init__(self, views):
        self.s = Solver()
        self.views = views

    # Outputs a list of views in the same format as the input
    def constraint_to_coords(self):
        num_frameless = len(filter(lambda view: view.frame_constraint == None, self.views))
