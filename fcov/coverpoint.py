# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

import itertools
from collections import defaultdict
from enum import Enum
from types import SimpleNamespace
from typing import Iterable, Iterator

from rich.console import Console
from rich.table import Table

from .common.chain import OpenLink, Link
from .link import CovDef, CovRun
from .covergroup import CoverBase
from .context import CoverageContext

from .axis import Axis
from .cursor import Cursor
from .goal import GoalItem
from .triggers import CoverageTriggers


class GOAL(Enum):
    ILLEGAL = -1
    IGNORE = 0
    DEFAULT = 10


class Coverpoint(CoverBase):
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
        self.axes: list[Axis] = []  # TODO make a dict
        # Number of hits for each bucket
        self.cvg_hits = defaultdict(int)
        # Dictionary of defined goals
        self._goal_dict = {"DEFAULT": GoalItem()}
        # Dictionary of goals for each bucket
        self._cvg_goals = {}
        # Instance of Cursor class to increment hit count for a bucket
        self.cursor = Cursor(self)

        self.setup(ctx=CoverageContext.get())

        self.axis_names = [x.name for x in self.axes]
        goals = SimpleNamespace(**self._goal_dict)
        for cursor in self.all_axis_value_combinations():
            bucket = SimpleNamespace(**dict(zip(self.axis_names, cursor, strict=True)))
            goal = self.apply_goals(bucket, goals)
            if goal:
                self._cvg_goals[cursor] = goal

    def setup(self, ctx: SimpleNamespace):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

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

    def add_goal(self, name, target, description):
        formatted_name = name.upper()
        if formatted_name in self._goal_dict:
            raise Exception(f'Goal "{formatted_name}" already defined for this coverpoint')
        self._goal_dict[formatted_name] = GoalItem(name, target, description)

    def apply_goals(self, bucket=None, goals=None):
        if len(self._goal_dict) == 1:
            return self._goal_dict["DEFAULT"]
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def get_goal(self, cursor):
        if cursor in self._cvg_goals:
            return self._cvg_goals[cursor]
        else:
            return self._goal_dict['DEFAULT']

    def chain_def(self, start: OpenLink[CovDef] | None = None) -> Link[CovDef]:
        start = start or OpenLink(CovDef())

        child_start = start.link_down()
        child_close = None

        for axis in self.axes:
            child_close = axis.chain(child_start)
            child_start = child_close.link_across()

        for goal in self._goal_dict.values():
            child_close = goal.chain(child_start)
            child_start = child_close.link_across()

        buckets = 0
        target = 0
        target_buckets = 0
        for cursor in self.all_axis_value_combinations():
            bucket_target = self.get_goal(cursor).target
            if bucket_target > 0:
                target += bucket_target
                target_buckets += 1
            buckets += 1

        link = CovDef(
            point=1,
            bucket=buckets, 
            target=target,
            target_buckets=target_buckets
        )

        return start.close(self, 
                           child=child_close,
                           link=link,
                           typ=Coverpoint)

    def chain_run(self, start: OpenLink[CovRun] | None = None) -> Link[CovRun]:
        start = start or OpenLink(CovRun())

        buckets = 0
        hits = 0
        hit_buckets = 0
        full_buckets = 0
        for cursor in self.all_axis_value_combinations():
            bucket_target = self.get_goal(cursor).target
            bucket_hits = self.cvg_hits[cursor]

            if bucket_target > 0:
                bucket_hits = min(bucket_target, bucket_hits)
                if bucket_hits > 0:
                    hit_buckets += 1
                    if bucket_hits == bucket_target:
                        full_buckets += 1
                    hits += bucket_hits
            buckets += 1

        link = CovRun(
            point=1,
            bucket=buckets,
            hits=hits,
            hit_buckets=hit_buckets,
            full_buckets=full_buckets
        )

        return start.close(self, 
                           link=link,
                           typ=Coverpoint)

    def bucket_goals(self):
        for cursor in self.all_axis_value_combinations():
            yield self.get_goal(cursor).name

    def bucket_hits(self):
        for cursor in self.all_axis_value_combinations():
            yield self.cvg_hits[cursor]

    def serialize_point_hits(self):
        hits = 0
        for cursor in self.all_axis_value_combinations():
            target = self.get_goal(cursor).target
            if target > 0:
                hits += min(target, self.cvg_hits[cursor])
        yield hits

    def _debug_coverage(self):
       
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
                str(goal.target),
                percentage_hit(hits, goal.target),
                goal.name,
                goal.description,
            ]

            table.add_row(*data)

        console = Console()
        console.print(table)