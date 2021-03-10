from enum import IntEnum
from copy import deepcopy

class ViewType(IntEnum):
    VStack = 0
    HStack = 1
    Leaf = 2

class View:
    def __init__(self, top_left, bot_right, view_type=ViewType.Leaf):
        self.top_left = top_left
        self.bot_right = bot_right
        self.view_type = view_type

        # Constraints for H/VStack
        self.spacing_constraint = 0
        # Constraints for leaf views
        self.padding_constraint = [[0, 0], [0, 0]]
        self.frame_constraint = None
        # 0 = left, 1 = center, 2 = right
        self.alignment = 1

    def __eq__(self, other):
        return self.top_left == other.top_left and self.bot_right == other.bot_right

    def __str__(self):
        return str(self.top_left) + ", " + str(self.bot_right) + " " + str(self.view_type)

    # 0 for height, 1 for width
    def size(self, axis):
        return self.bot_right[axis] - self.top_left[axis]

    def center(self, axis):
        return (self.bot_right[axis] + self.top_left[axis]) / 2

    def is_framed(self, axis):
        return self.frame_constraint != None \
               and self.frame_constraint[axis] != None \
               and self.frame_constraint[axis] != 0

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

    def deepcopy(self):
        return View(deepcopy(self.top_left), deepcopy(self.bot_right), self.view_type)

    def move(self, diff):
        '''Moves top left to new top_left, changing bot_right as well as children
        '''
        def add(a, b):
            return [new + old for new, old in zip(a, b)]

        self.top_left = add(self.top_left, diff)
        self.bot_right = add(self.bot_right, diff)

