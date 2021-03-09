from view import *
from constraint_solver import *

class Hierarchy(View):
    def __init__(self, top_left, bot_right, view_type=ViewType.VStack, children=[]):
        super().__init__(top_left, bot_right, view_type)
        self.children = children

    def solve(self):
        print([str(child) for child in [self] + self.children])
        ConstraintSolver([self] + self.children).solve()
        for child in self.children:
            if isinstance(child, Hierarchy):
                child.solve()


    def to_swiftui(self):
        #TODO: convert view hierarchy's constraints to swiftui
        return ""

def divide_views(views, axis):
    '''Divides the given views by the axis where possible.
    axis: 0 = y, 1 = x
    returns: hiearchy, hierarchy_complexity
    '''
    views = sorted(views, key=lambda view: view.bot_right[axis])
    divided = []
    while len(views) > 0:
        cur = views.pop(0)
        section = [cur]
        while len(views) > 0 and min([view.top_left[axis] for view in views]) < cur.bot_right[axis]:
            cur = views.pop(0)
            section.append(cur)
        divided.append(section)

    hierarchy_complexity = 1
    children = []
    for section in divided:
        if len(section) == 1:
            children.extend(section)
        else:
            sub_root, complexity = divide_views(section, (axis + 1) % 2)
            children.append(sub_root)
            hierarchy_complexity += complexity
    top_left = [min([view.top_left[0] for view in children]), min([view.top_left[1] for view in children])]
    bot_right = [max([view.bot_right[0] for view in children]), max([view.bot_right[1] for view in children])]
    root_hierarchy = Hierarchy(top_left, bot_right, view_type=ViewType(axis), children=children)
    return root_hierarchy, hierarchy_complexity

def infer_hierarchy(views):
    '''Takes in a flat list of views and infers hierarchy'''
    root = views.pop(0)
    vert_hierarchy, vert_complexity = divide_views(views, 0)
    hori_hierarchy, hori_complexity = divide_views(views, 1)
    (_, hierarchy) = min((vert_complexity, vert_hierarchy), (hori_complexity, hori_hierarchy))
    # We do this to enforce that the root view has the same dimensions as supplied. Otherwise,
    # the default behavior is that the root view will be the smallest it can be such that it can
    # fit all of its subviews.
    hierarchy.top_left = root.top_left
    hierarchy.bot_right = root.bot_right
    return hierarchy
