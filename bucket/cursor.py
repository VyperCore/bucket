# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

class Cursor:
    # This class takes all the axes and their values
    # and inrements the coverage for that cross

    def __init__(
        self,
        parent,
    ):
        self.parent = parent
        self.clear()

    def __call__(self):
        ...

    def clear(self):
        '''
        This function clears the cursor. No values will be retained for any axis
        '''
        self.axis_values = {}

    def __enter__(self):
        # 'with' allows the cursor to be wiped before use
        self.clear()
        return self

    def __exit__(self, *args):
        # 'with' allows the cursor to be wiped after use
        self.clear()

    def increment(self):
        '''
        This function will attempt to increment the hit count for the combination of axis
        values specified. All axes need to have been set to a valid value, if not an error
        will be generated.
        '''
        assert len(self.axis_values) == len(
            self.parent.axes
        ), "Incorrect number of axes have been set"
        cursor_list = []
        for i, axis in enumerate(self.parent.axes):
            if axis.name in self.axis_values:
                result = self.parent.axes[i].get_named_value(self.axis_values[axis.name])
                cursor_list.append(result)
            else:
                raise Exception(f"Axis {axis.name} has not been set")

        # make it a tuple, increment cvg_hits
        cursor_tuple = tuple(cursor_list)
        # Check for any applied goals
        cursor_goal = self.parent.get_goal(cursor_tuple)

        # If the bucket goal is defined as IGNORE, nothing happens.
        # If the bucket goal is defined as ILLEGAL, an error is printed out
        # Else the bucket is incremented
        if cursor_goal.target > 0:
            self.parent.increment_hit_count(cursor_tuple)
        elif cursor_goal.target < 0:
            print(f"Illegal bucket '{self.parent.name}.{cursor_goal.name}' hit!")
            print(f"  Cursor: {dict(zip(self.parent.axis_names, list(cursor_tuple), strict=True))}")

    def set_cursor(self, **kwargs):
        # Update dictionary of axis values
        # Overwrite existing axis values if same key set again
        self.axis_values |= kwargs