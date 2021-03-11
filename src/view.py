from enum import IntEnum
from copy import deepcopy
import math

VIEW_DEFAULT = "Color.black"

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

    def truncate_values(self):
        self.spacing_constraint = round(self.spacing_constraint, 1)
        for i in range(2):
            if self.is_framed(i):
                self.frame_constraint[i] = round(self.frame_constraint[i], 1)
        for i in range(2):
            for j in range(2):
                self.padding_constraint[i][j] = round(self.padding_constraint[i][j], 1)

    def to_swiftui(self):
        self.truncate_values()
        fargs = []
        if self.is_framed(1):
            fargs.append("width: " + str(self.frame_constraint[1]))
        if self.is_framed(0):
            fargs.append("height: " + str(self.frame_constraint[0]))
        frame = (f".frame({', '.join(fargs)})") if len(fargs) > 0 else ""

        padstr = ""
        padding = self.padding_constraint
        if padding[0][0] == padding[0][1] and padding[0][0] > 0:
            padstr += f".padding(.vertical, {padding[0][0]})"
        else:
            if padding[0][0] > 0:
                padstr += f".padding(.top, {padding[0][0]})"
            if padding[0][1] > 0:
                padstr += f".padding(.bottom, {padding[0][1]})"

        if padding[1][0] == padding[1][1] and padding[1][0] > 0:
            padstr += f".padding(.horizontal, {padding[1][0]})"
        else:
            if padding[1][0] > 0:
                padstr += f".padding(.leading, {padding[1][0]})"
            if padding[1][1] > 0:
                padstr += f".padding(.trailing, {padding[1][1]})"

        return VIEW_DEFAULT + frame + padstr
