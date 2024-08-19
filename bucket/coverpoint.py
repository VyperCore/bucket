# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

import hashlib
import itertools
from collections import defaultdict
from enum import Enum
from types import SimpleNamespace

from rich.console import Console
from rich.table import Table

from .axis import Axis
from .bucket import Bucket
from .common.chain import Link, OpenLink
from .context import CoverageContext
from .covergroup import CoverBase
from .goal import GoalItem
from .link import CovDef, CovRun
from .triggers import CoverageTriggers
from typing import Callable


class GOAL(Enum):
    ILLEGAL = -1
    IGNORE = 0
    DEFAULT = 10


class Coverpoint(CoverBase):
    bucket: Bucket
    """
    This Bucket class is used for incrementing the hit count on a given bucket.

    Example 1 (using 'with' to clear the bucket after each use)::

        with self.bucket as bucket:
            bucket.set_axes(
                name=trace['Name'],
                age=trace['Age'],
                size=trace['Weight']
            )
            bucket.hit()

    Example 2 (Showing how the bucket axes can be set multiple times, and old values retained)::

            self.bucket.clear()
            self.bucket.set_axes(
                name=trace['Name'],
                age=trace['Age'],
            )
            for toy in trace['Toys']:
                bucket.set_axes(toy = toy)
                self.bucket.hit()

    Example 3 (demonstrating passing in all axis values into hit, rather than calling set_axes)::

            self.bucket.hit(
                name=trace['Name'],
                age=trace['Age'],
                size=trace['Weight']
            )

    """

    def __init__(self, name: str, description: str, trigger=None):
        self.name = name
        self.description = description
        self.trigger = CoverageTriggers.ALL if trigger is None else trigger
        self.active = True

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
        # Instance of Bucket class to increment hit count for a bucket
        self.bucket = Bucket(self)

        self._setup()

        self.sha = hashlib.sha256((self.name + self.description).encode())
        self.axis_names = [x.name for x in self.axes]
        goals = SimpleNamespace(**self._goal_dict)
        for combination in self._all_axis_value_combinations():
            bucket = SimpleNamespace(
                **dict(zip(self.axis_names, combination, strict=True))
            )
            if goal := self.apply_goals(bucket, goals):
                self._cvg_goals[combination] = goal
            else:
                goal = self._goal_dict["DEFAULT"]
            self.sha.update(goal.sha.digest())


    def _setup(self):
        """
        This calls the user defined setup() plus any other setup required
        """
        self.setup(ctx=CoverageContext.get())

    def setup(self, ctx: SimpleNamespace):
        """
        This function needs to be implemented for each coverpoint. Axes and goals are added here.
        See example.py for how to use
        """
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def _apply_filter(self, matcher: Callable[[CoverBase], bool], match_state: bool | None, mismatch_state: bool | None):
        if matcher(self) and match_state is not None:
            self.active = match_state
        elif mismatch_state is not None:
            self.active = mismatch_state
        return self.active

    def _sample(self, trace):
        """
        Call user defined sample function if active
        """
        if self.active:
            self.sample(trace)

    def _all_axis_value_combinations(self):
        """
        Iterate over all possible axis value combinations
        """
        axis_values = []
        for axis in self.axes:
            axis_values.append(list(axis.values.keys()))
        yield from itertools.product(*axis_values)

    def _increment_hit_count(self, bucket: tuple, hits: int = 1):
        """
        Increment hit count for the specified bucket. Default is +1
        """
        self.cvg_hits[bucket] += hits

    def add_axis(self, name: str, values: dict | list | set | tuple, description: str):
        """
        Add axis with values to process later
        """
        self.axes.append(Axis(name, values, description))

    def add_goal(
        self,
        name: str,
        description: str,
        illegal: bool = False,
        ignore: bool = False,
        target: int | None = None,
    ):
        formatted_name = name.upper()
        assert (
            formatted_name not in self._goal_dict
        ), f'Goal "{formatted_name}" already defined for this coverpoint'
        assert (
            sum([illegal, ignore, (target is not None)]) <= 1
        ), "Only one option may be chosen: illegal, ignore or target"
        assert target is None or target > 0, "If target is supplied, it must be 1+"

        if illegal:
            target = -1
        elif ignore:
            target = 0
        elif target is None:
            # This shouldn't be hardcoded, something that can be overridden would be good
            target = 10

        self._goal_dict[formatted_name] = GoalItem(name, target, description)

    def apply_goals(
        self, bucket: SimpleNamespace, goals: SimpleNamespace
    ):
        """
        If coverpoint goals are defined, this function must be implemented by the coverpoint.
        If no goals are defined, then 'DEFAULT' will be applied
        See example.py for how to use.
        """
        if len(self._goal_dict) == 1:
            return self._goal_dict["DEFAULT"]
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def _get_goal(self, bucket: tuple):
        """
        Retrieve goal for a given bucket
        """
        if bucket in self._cvg_goals:
            return self._cvg_goals[bucket]
        else:
            return self._goal_dict["DEFAULT"]

    def _chain_def(self, start: OpenLink[CovDef] | None = None) -> Link[CovDef]:
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
        for bucket in self._all_axis_value_combinations():
            bucket_target = self._get_goal(bucket).target
            if bucket_target > 0:
                target += bucket_target
                target_buckets += 1
            buckets += 1

        link = CovDef(
            point=1,
            bucket=buckets,
            target=target,
            target_buckets=target_buckets,
            sha=self.sha,
        )

        return start.close(self, child=child_close, link=link, typ=CoverBase)

    def _chain_run(self, start: OpenLink[CovRun] | None = None) -> Link[CovRun]:
        start = start or OpenLink(CovRun())

        buckets = 0
        hits = 0
        hit_buckets = 0
        full_buckets = 0
        for bucket in self._all_axis_value_combinations():
            bucket_target = self._get_goal(bucket).target
            bucket_hits = self.cvg_hits[bucket]

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
            full_buckets=full_buckets,
        )

        return start.close(self, link=link, typ=CoverBase)

    def _bucket_goals(self):
        """
        Get goals for each bucket
        """
        for bucket in self._all_axis_value_combinations():
            yield self._get_goal(bucket).name

    def _bucket_hits(self):
        """
        Get hits for each bucket
        """
        for bucket in self._all_axis_value_combinations():
            yield self.cvg_hits[bucket]

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
        for bucket in self._all_axis_value_combinations():
            hits = self.cvg_hits[bucket]
            goal = self._get_goal(bucket)
            data = [
                *list(bucket),
                str(hits),
                str(goal.target),
                percentage_hit(hits, goal.target),
                goal.name,
                goal.description,
            ]

            table.add_row(*data)

        console = Console()
        console.print(table)
