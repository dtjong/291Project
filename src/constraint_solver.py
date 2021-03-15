from z3 import *
from view import *

# Constraint Solver for one level (no hierarchy)
class ConstraintSolver:
    def __init__(self, views):
        self.views = views

    def solve(self):
        s = Optimize()
        Spacing = Real('Spacing')
        # 0 = leading, 1 = center, 2 = trailing
        Alignment = Int('Alignment')
        Frames = [[Real('FrameHeight' + str(i)) for i in range(len(self.views) - 1)],
                  [Real('FrameWidth' + str(i)) for i in range(len(self.views) - 1)]]
        PrePad = [[Real('PadTop' + str(i)) for i in range(len(self.views) - 1)],
                  [Real('PadLeft' + str(i)) for i in range(len(self.views) - 1)]]
        PostPad = [[Real('PadBot' + str(i)) for i in range(len(self.views) - 1)],
                  [Real('PadRight' + str(i)) for i in range(len(self.views) - 1)]]

        s.add(Spacing >= 0)
        s.add(Alignment >= 0)
        s.add(Alignment <= 2)
        def nonzero_list(l):
            for prop in l[0] + l[1]:
                s.add(prop >= 0)
        nonzero_list(Frames)
        nonzero_list(PrePad)
        nonzero_list(PostPad)

        root = self.views[0]
        major_axis = int(root.view_type)
        minor_axis = int(ViewType.HStack if root.view_type == ViewType.VStack else ViewType.VStack)

        stack_top_left = root.top_left[major_axis] + (root.size(major_axis) - (Sum(Frames[major_axis]) \
                         + Sum(PrePad[major_axis]) \
                         + Sum(PostPad[major_axis]) \
                         + Spacing * (len(self.views) - 2))) / 2
        # s.add(stack_top_left - root.top_left[major_axis] >= -3)

        unframed_vmode = 0

        for i, view in enumerate(self.views[1:]):
            fsize = (root.size(major_axis) \
                     - Spacing * (len(self.views) - 2) \
                     - Sum(PrePad[major_axis]) \
                     - Sum(PostPad[major_axis]) \
                     - Sum(Frames[major_axis])) \
                     / Sum([If(sz == 0, 1, 0) for sz in Frames[major_axis]])
            top_major = Sum(Frames[major_axis][:i]) \
                      + Sum(PrePad[major_axis][:i+1]) \
                      + Sum(PostPad[major_axis][:i]) \
                      + Sum([If(sz == 0, 1, 0) for sz in Frames[major_axis][:i]]) * fsize \
                      + Spacing * i \
                      + If(Sum([If(sz == 0, 1, 0) for sz in Frames[major_axis]]) == 0, stack_top_left, root.top_left[major_axis])
            bot_major = top_major + If(Frames[major_axis][i] == 0, fsize,
                                       Frames[major_axis][i])

            top_minor_nf = root.top_left[minor_axis] + PrePad[minor_axis][i]
            bot_minor_nf = root.bot_right[minor_axis] - PostPad[minor_axis][i]

            top_minor_alead = root.top_left[minor_axis] + PrePad[minor_axis][i]
            bot_minor_alead = top_minor_alead + Frames[minor_axis][i]

            top_minor_acenter = (root.bot_right[minor_axis] - root.top_left[minor_axis] \
                                - PrePad[minor_axis][i] - PostPad[minor_axis][i] - Frames[minor_axis][i]) / 2 \
                                + top_minor_alead
            bot_minor_acenter = top_minor_acenter + Frames[minor_axis][i]

            bot_minor_atrail = root.bot_right[minor_axis] - PostPad[minor_axis][i]
            top_minor_atrail = bot_minor_atrail - Frames[minor_axis][i]

            s.add(view.top_left[major_axis] == top_major)
            s.add(view.bot_right[major_axis] == bot_major)
            s.add(view.top_left[minor_axis] == If(Frames[minor_axis][i] == 0,
                                                  top_minor_nf,
                                               If(Alignment == 0,
                                                  top_minor_alead,
                                               If(Alignment == 1,
                                                  top_minor_acenter,
                                                  top_minor_atrail))))
            s.add(view.bot_right[minor_axis] == If(Frames[minor_axis][i] == 0,
                                                  bot_minor_nf,
                                               If(Alignment == 0,
                                                  bot_minor_alead,
                                               If(Alignment == 1,
                                                  bot_minor_acenter,
                                                  bot_minor_atrail))))
            # assert that frame matches
            if view.view_mode == ViewMode.Framed:
                s.add(Frames[major_axis][i] > 0)
                s.add(Frames[minor_axis][i] > 0)
            else:
                unframed_vmode += If(Frames[major_axis][i] == 0, 1, 0)
                unframed_vmode += If(Frames[minor_axis][i] == 0, 1, 0)
        # Optimization
        # for view in self.views[1:]:
            # if view.view_mode == ViewMode.Unframed:
                # s.maximize(unframed_vmode)
                # break

        # constrained_frames = Sum([If(sz == 0, 0, 1) for sz in Frames[major_axis] + Frames[minor_axis]])
        # s.minimize(constrained_frames)
        # maximize matching frames
        matching_frames = 0
        for i in range(len(Frames[0])):
            for j in range(i+1, len(Frames[0])):
                matching_frames += If(Frames[0][i] == Frames[0][j] and
                                      Frames[1][i] == Frames[1][j], 1, 0)
        s.maximize(matching_frames)

        symmetric_padding = Sum([If(pre == post, 1, 0) for pre, post in
                                 zip(PrePad[minor_axis] + PrePad[major_axis],
                                     PostPad[minor_axis] + PostPad[major_axis])])
        s.maximize(symmetric_padding)
        # prefer center alignment over others
        is_centered = If(Alignment == 1, 1, 0)
        s.maximize(is_centered)

        if len(Frames[0]) > 1:
            s.maximize(Spacing)

        if s.check() == sat:
            m = s.model()
            print(m)
            def get_long(realval):
                return m[realval].numerator_as_long() / m[realval].denominator_as_long()
            view.alignment = m[Alignment].as_long()
            root.gen_spacing(get_long(Spacing))
            for i, view in enumerate(self.views[1:]):
                view.gen_frame(get_long(Frames[0][i]), get_long(Frames[1][i]))
                view.gen_padding(get_long(PrePad[0][i]),
                                 get_long(PostPad[0][i]),
                                 get_long(PrePad[1][i]),
                                 get_long(PostPad[1][i]))
            print(self.verify())
        else:
            print("UNSAT")

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
