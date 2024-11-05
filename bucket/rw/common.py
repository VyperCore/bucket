# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from typing import Any, Iterable, NamedTuple, Protocol

from ..common.chain import Link
from ..link import CovDef, CovRun

###############################################################################
# Coverage information in tuple form, which is used to interface between
# different readers and writers.
###############################################################################


class PointTuple(NamedTuple):
    start: int
    depth: int
    end: int
    axis_start: int
    axis_end: int
    axis_value_start: int
    axis_value_end: int
    goal_start: int
    goal_end: int
    bucket_start: int
    bucket_end: int
    target: int
    target_buckets: int
    name: str
    description: str

    @classmethod
    def from_link(cls, link: Link[CovDef]):
        return cls(
            start=link.start.point,
            depth=link.depth,
            end=link.end.point,
            axis_start=link.start.axis,
            axis_end=link.end.axis,
            axis_value_start=link.start.axis_value,
            axis_value_end=link.end.axis_value,
            goal_start=link.start.goal,
            goal_end=link.end.goal,
            bucket_start=link.start.bucket,
            bucket_end=link.end.bucket,
            target=link.end.target - link.start.target,
            target_buckets=link.end.target_buckets - link.start.target_buckets,
            name=link.item._name,
            description=link.item._description,
        )


class BucketGoalTuple(NamedTuple):
    start: int
    goal: int


class AxisTuple(NamedTuple):
    start: int
    value_start: int
    value_end: int
    name: str
    description: str

    @classmethod
    def from_link(cls, link: Link[CovDef]):
        return cls(
            start=link.start.axis,
            value_start=link.start.axis_value,
            value_end=link.end.axis_value,
            name=link.item.name,
            description=link.item.description,
        )


class AxisValueTuple(NamedTuple):
    start: int
    value: str


class GoalTuple(NamedTuple):
    start: int
    target: int
    name: str
    description: str

    @classmethod
    def from_link(cls, link: Link[CovDef]):
        return cls(
            start=link.start.goal,
            target=link.item.target,
            name=link.item.name,
            description=link.item.description,
        )


class PointHitTuple(NamedTuple):
    start: int
    depth: int
    hits: int
    hit_buckets: int
    full_buckets: int

    @classmethod
    def from_link(cls, link: Link[CovRun]):
        return cls(
            start=link.start.point,
            depth=link.depth,
            hits=link.end.hits - link.start.hits,
            hit_buckets=link.end.hit_buckets - link.start.hit_buckets,
            full_buckets=link.end.full_buckets - link.start.full_buckets,
        )


class BucketHitTuple(NamedTuple):
    start: int
    hits: int


###############################################################################
# Inferface definitions
###############################################################################


class Reading(Protocol):
    """
    Readings allow us to access coverage from a record consistently, without
    having to worry about the storage backend.
    """

    def get_def_sha(self) -> str: ...
    def get_rec_sha(self) -> str: ...
    def iter_points(
        self, start: int = 0, end: int | None = None, depth: int = 0
    ) -> Iterable[PointTuple]: ...
    def iter_bucket_goals(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[BucketGoalTuple]: ...
    def iter_axes(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[AxisTuple]: ...
    def iter_axis_values(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[AxisValueTuple]: ...
    def iter_goals(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[GoalTuple]: ...
    def iter_point_hits(
        self, start: int = 0, end: int | None = None, depth: int = 0
    ) -> Iterable[PointHitTuple]: ...
    def iter_bucket_hits(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[BucketHitTuple]: ...


class Reader(Protocol):
    """
    Readers read from a backend to produce readings.
    """

    def read(self, rec_ref) -> Reading: ...


class Writer(Protocol):
    """
    Writers write to a backend from a reading.
    """

    def write(self, reading) -> Any: ...


###############################################################################
# Utility readings
###############################################################################


class PuppetReading(Reading):
    """
    Utility reading which stores coverage information directly rather than
    acting as an interface to other storage.
    """

    def __init__(self):
        self.points: list[PointTuple] = []
        self.bucket_goals: list[BucketGoalTuple] = []
        self.axes: list[AxisTuple] = []
        self.axis_values: list[AxisValueTuple] = []
        self.goals: list[GoalTuple] = []
        self.point_hits: list[PointHitTuple] = []
        self.bucket_hits: list[BucketHitTuple] = []
        self.def_sha = None
        self.rec_sha = None

    def get_def_sha(self) -> str:
        if self.def_sha is None:
            raise RuntimeError("def_sha not set")
        return self.def_sha

    def get_rec_sha(self) -> str:
        if self.rec_sha is None:
            raise RuntimeError("rec_sha not set")
        return self.rec_sha

    def iter_points(
        self, start: int = 0, end: int | None = None, depth: int = 0
    ) -> Iterable[PointTuple]:
        offset_start = start + depth
        offset_end = None if end is None else end + depth
        yield from self.points[offset_start:offset_end]

    def iter_bucket_goals(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[BucketGoalTuple]:
        yield from self.bucket_goals[start:end]

    def iter_axes(self, start: int = 0, end: int | None = None) -> Iterable[AxisTuple]:
        yield from self.axes[start:end]

    def iter_axis_values(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[AxisValueTuple]:
        yield from self.axis_values[start:end]

    def iter_goals(self, start: int = 0, end: int | None = None) -> Iterable[GoalTuple]:
        yield from self.goals[start:end]

    def iter_point_hits(
        self, start: int = 0, end: int | None = None, depth: int = 0
    ) -> Iterable[PointHitTuple]:
        offset_start = start + depth
        offset_end = None if end is None else end + depth
        yield from self.point_hits[offset_start:offset_end]

    def iter_bucket_hits(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[BucketHitTuple]:
        yield from self.bucket_hits[start:end]


class MergeReading(Reading):
    """
    Utility reading which merges data from other readings. It takes one master
    reading, which all others must match.
    """

    def __init__(self, master: Reading, *others: Reading):
        super().__init__()
        self.master = master

        self.bucket_hits: list[int] = []
        for bucket_hit in master.iter_bucket_hits():
            self.bucket_hits.append(bucket_hit.hits)

        goal_targets: list[int] = []
        for goal in master.iter_goals():
            goal_targets.append(goal.target)

        self.bucket_targets: list[int] = []
        for bucket_goal in master.iter_bucket_goals():
            self.bucket_targets.append(goal_targets[bucket_goal.goal])

        if others:
            self.merge(*others)

    def get_def_sha(self) -> str:
        return self.master.get_def_sha()

    def get_rec_sha(self) -> str:
        return self.master.get_rec_sha()

    def iter_points(
        self, start: int = 0, end: int | None = None, depth: int = 0
    ) -> Iterable[PointTuple]:
        yield from self.master.iter_points(start, end, depth)

    def iter_bucket_goals(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[BucketGoalTuple]:
        yield from self.master.iter_bucket_goals(start, end)

    def iter_axes(self, start: int = 0, end: int | None = None) -> Iterable[AxisTuple]:
        yield from self.master.iter_axes(start, end)

    def iter_axis_values(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[AxisValueTuple]:
        yield from self.master.iter_axis_values(start, end)

    def iter_goals(self, start: int = 0, end: int | None = None) -> Iterable[GoalTuple]:
        yield from self.master.iter_goals(start, end)

    def iter_bucket_hits(
        self, start: int = 0, end: int | None = None
    ) -> Iterable[BucketHitTuple]:
        for offset, hits in enumerate(self.bucket_hits[start:end]):
            yield BucketHitTuple(start + offset, hits)

    def iter_point_hits(
        self, start: int = 0, end: int | None = None, depth: int = 0
    ) -> Iterable[PointHitTuple]:
        for point in self.iter_points(start, end, depth):
            hits = 0
            hit_buckets = 0
            full_buckets = 0
            for bucket_hit in self.iter_bucket_hits(
                point.bucket_start, point.bucket_end
            ):
                target = self.bucket_targets[bucket_hit.start]
                if target > 0:
                    bucket_hits = min(bucket_hit.hits, target)
                    if bucket_hit.hits > 0:
                        hit_buckets += 1
                        if bucket_hits == target:
                            full_buckets += 1
                        hits += bucket_hits

            yield PointHitTuple(
                start=point.start,
                depth=point.depth,
                hits=hits,
                hit_buckets=hit_buckets,
                full_buckets=full_buckets,
            )

    def merge(self, *readings: Reading):
        """
        Merge additional readings post init
        """
        master_def_sha = self.get_def_sha()
        master_rec_sha = self.get_rec_sha()

        for reading in readings:
            if reading.get_def_sha() != master_def_sha:
                raise RuntimeError(
                    "Tried to merge coverage with two different definition hashes!"
                )

            if reading.get_rec_sha() != master_rec_sha:
                raise RuntimeError(
                    "Tried to merge coverage with two different record hashes!"
                )

            for bucket_hit in reading.iter_bucket_hits():
                self.bucket_hits[bucket_hit.start] += bucket_hit.hits
