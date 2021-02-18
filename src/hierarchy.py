from view import *
from constraint_solver import *

class Hierarchy(View):
    def __init__(self, top_left, bot_right, view_type=ViewType.VStack, children=[]):
        super().__init__(top_left, bot_right, view_type)
        self.children = children

    def solve(self):
        ConstraintSolver([self] + self.children).solve()
        for child in children:
            if isinstance(child, Hierarchy):
                child.solve()

    def to_swiftui(self):
        #TODO: convert view hierarchy's constraints to swiftui
        pass
