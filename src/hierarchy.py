from view import *
from constraint_solver import *
from functools import reduce
import statistics
from copy import deepcopy

class Hierarchy(View):
    class size_group:
        def __init__(self, view, axis):
            self.axis = axis
            self.mean = view.size(axis)
            self.views = [view]

        def append(self, view):
            self.mean *= len(self.views) / (len(self.views) + 1)
            self.mean += view.size(self.axis) / (len(self.views) + 1)
            self.views.append(view)

        def pop(self):
            view = self.views.pop()
            self.mean -= view.size(self.axis) / (len(self.views) + 1)
            self.mean *= (len(self.views) + 1) / len(self.views)
            return view

        def variance(self):
            return statistics.variance([view.size(self.axis) for view in self.views], self.mean)

        def can_append(self, view, tolerance):
            self.append(view)
            valid = self.variance() < tolerance
            self.pop()
            return valid

        def enforce(self):
            # sets size of all views to group's mean
            for view in self.views:
                view.bot_right[self.axis] = view.top_left[self.axis] + self.mean

    def __init__(self, top_left, bot_right, view_type=ViewType.VStack, children=[]):
        super().__init__(top_left, bot_right, view_type)
        self.children = children

    def flatlist(self):
        l =  [child.flatlist() if isinstance(child, Hierarchy) else [child] for child in self.children]
        return reduce(lambda a, b: a + b, l)

    def solve(self):
        print([str(child) for child in [self] + self.children])
        ConstraintSolver([self] + self.children).solve()
        for child in self.children:
            if isinstance(child, Hierarchy):
                child.solve()

    def cleanse(self):
        '''Cleans the user-inputted data to match what they likely intended to
        draw. General workflow is cleanse -> solve -> to_swiftui
        '''
        # agree on size
        print(self)
        SIZE_VARIANCE_TOLERANCE = 50
        for axis in [0, 1]:
            size_groups = []
            for view in self.children:
                # We don't want to include hierarchies in this calculation
                # because it is unlikely that the user wants it to be the same
                # size, and because it may mess with child views.
                if isinstance(view, Hierarchy):
                    continue
                if len(size_groups) == 0:
                    size_groups.append(self.size_group(view, axis))
                else:
                    size_groups = sorted(size_groups, key=lambda group: abs(group.mean - view.size(axis)))
                    if size_groups[0].can_append(view, SIZE_VARIANCE_TOLERANCE):
                        size_groups[0].append(view)
                    else:
                        size_groups.append(self.size_group(view, axis))
            for g in size_groups:
                g.enforce()

        # snap position
        minor_axis = (int(self.view_type) + 1) % 2
        leading = self.top_left[minor_axis]
        trailing = self.bot_right[minor_axis]
        center = (leading + trailing) / 2
        for view in self.children:
            leaddist = abs(leading - view.top_left[minor_axis])
            traildist = abs(trailing - view.bot_right[minor_axis])
            centdist = abs(center - view.center(minor_axis))
            diff = [0, 0]
            # if leaddist < traildist and leaddist < centdist:
                # diff[minor_axis] = leading - view.top_left[minor_axis]
            # elif traildist < centdist:
                # diff[minor_axis] = trailing - view.bot_right[minor_axis]
            # else:
                # diff[minor_axis] = center - view.center(minor_axis)
            diff[minor_axis] = center - view.center(minor_axis)
            view.move(diff)

        for child in self.children:
            if isinstance(child, Hierarchy):
                child.cleanse()

    def to_swiftui(self):
        #TODO: convert view hierarchy's constraints to swiftui
        return ""

    def deepcopy(self):
        children = [child.deepcopy() for child in self.children]
        return Hierarchy(deepcopy(self.top_left), deepcopy(self.bot_right), self.view_type, children=children)

    def move(self, diff):
        super().move(diff)
        for child in self.children:
            child.move(diff)

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
