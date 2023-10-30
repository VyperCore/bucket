import itertools
from collections import defaultdict
from enum import Enum
from types import SimpleNamespace

from rich.console import Console
from rich.table import Table

from .axis import Axis
from .cursor import Cursor
from .goal import GoalItem
from .triggers import CoverageTriggers


class GOAL(Enum):
    ILLEGAL = -1
    IGNORE = 0
    DEFAULT = 10


class Coverpoint:
    # coverpoints_by_trigger = defaultdict(set)

    def __init__(self, name: str, description: str, trigger=None):
        self.name = name
        self.description = description
        self.trigger = CoverageTriggers.ALL if trigger is None else trigger

        # Sanity check name has been given. No default!
        assert isinstance(self.name, str), "Coverpoint name not provided"
        assert isinstance(self.description, str), "Coverpoint description not provided"
        print(f"{self.name}: {self.description}")

        # List of axes used by this coverpoint
        self.axes = []  # TODO make a dict
        # Number of hits for each bucket
        self.cvg_hits = defaultdict(int)
        # Dictionary of defined goals
        self._goal_dict = {"DEFAULT": GoalItem()}
        # Dictionary of goals for each bucket
        self._cvg_goals = {}
        # Instance of Cursor class to increment hit count for a bucket
        self.cursor = Cursor(self)

        self.setup()

        self.axis_names = [x.name for x in self.axes]
        # TODO Check if goalsDict only has 1 entry
        goals = SimpleNamespace(**self._goal_dict)
        for cursor in self.all_axis_value_combinations():
            bucket = SimpleNamespace(**dict(zip(self.axis_names, cursor, strict=True)))
            goal = self.apply_goals(bucket, goals)
            if goal:
                self._cvg_goals[cursor] = goal

    def all_axis_value_combinations(self):
        axis_values = []
        for axis in self.axes:
            axis_values.append(list(axis.values.keys()))
        yield from itertools.product(*axis_values)

    def increment_hit_count(self, cursor, hits=1):
        self.cvg_hits[cursor] += hits

    def add_axis(self, name, values, description):
        # Add axis with values to process later
        # Dicts should be ordered, so keep the order they are installed...
        self.axes.append(Axis(name, values, description))

    def add_goal(self, name, amount, description):
        formatted_name = name.upper()
        if formatted_name in self._goal_dict:
            raise Exception(f'Goal "{formatted_name}" already defined for this coverpoint')
        self._goal_dict[formatted_name] = GoalItem(name, amount, description)

    def apply_goals(self, bucket=None, goals=None):
        # This should be implemented by the coverpoint when requried
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def sample():
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def get_goal(self, cursor):
        if cursor in self._cvg_goals:
            return self._cvg_goals[cursor]
        else:
            return GoalItem()

    def export_coverage(self):
        # This should return all coverage in a useable format
        # or just axisName, cvg_hits and _goal_dict?
        # For now it prints
        self._debug_coverage()

    def _debug_coverage(self):
        def print_fixed_width_columns(data, column_width, header=False):
            formatted_item = ""
            for item in data:
                # Format each item with a fixed width
                formatted_item += f"| {item!s:{column_width}} "
            if header:
                length = len(formatted_item)
                print("-" * length)
            print(formatted_item)
            if header:
                print("-" * length)

        def percentage_hit(hits, goal):
            if goal >= 0:
                return f"{min((100*hits/goal), 100):.1f}%"
            else:
                return "-"

        table = Table(title=self.name.upper())

        header_names = [x.name for x in self.axes] + [
            "Total Hits",
            "Goal",
            "Percentage Hit",
            "Goal Name",
            "Goal Description",
        ]

        for header in header_names:
            table.add_column(header, justify="right", style="cyan", no_wrap=True)

        # Iterate over all buckets (even if unhit):
        for cursor in self.all_axis_value_combinations():
            hits = self.cvg_hits[cursor]
            goal = self.get_goal(cursor)
            data = [
                *list(cursor),
                str(hits),
                str(goal.amount),
                percentage_hit(hits, goal.amount),
                goal.name,
                goal.description,
            ]

            table.add_row(*data)

        console = Console()
        console.print(table)