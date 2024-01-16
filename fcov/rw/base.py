
from typing import Any, Iterable, NamedTuple, Protocol

from ..link import CovDef, CovRun
from ..common.chain import Link


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
            target=link.end.target-link.start.target,
            target_buckets=link.end.target_buckets-link.start.target_buckets,
            name=link.item.name,
            description=link.item.description
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
        return cls(start=link.start.axis,
                   value_start=link.start.axis_value,
                   value_end=link.end.axis_value,
                   name=link.item.name,
                   description=link.item.description
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
        return cls(start=link.start.goal,
                   target=link.item.target,
                   name=link.item.name,
                   description=link.item.description
        )

class PointHitTuple(NamedTuple):
    start: int
    depth: int
    hits: int
    hit_buckets: int
    full_buckets: int

    @classmethod
    def from_link(cls, link: Link[CovRun]):
        return cls(start=link.start.point,
                   depth=link.depth,
                   hits=link.end.hits-link.start.hits,
                   hit_buckets=link.end.hit_buckets-link.start.hit_buckets,
                   full_buckets=link.end.full_buckets-link.start.full_buckets,
        )


class BucketHitTuple(NamedTuple):
    start: int
    hits: int


class Reading(Protocol):
    def get_def_sha(self) -> str: ...
    def get_rec_sha(self) -> str: ...
    def iter_points(self, start: int=0, end: int|None=None) -> Iterable[PointTuple]: ...
    def iter_bucket_goals(self, start: int=0, end: int|None=None) -> Iterable[BucketGoalTuple]: ...
    def iter_axes(self, start: int=0, end: int|None=None) -> Iterable[AxisTuple]: ...
    def iter_axis_values(self, start: int=0, end: int|None=None) -> Iterable[AxisValueTuple]: ...
    def iter_goals(self, start: int=0, end: int|None=None) -> Iterable[GoalTuple]: ...
    def iter_point_hits(self, start: int=0, end: int|None=None) -> Iterable[PointHitTuple]: ...
    def iter_bucket_hits(self, start: int=0, end: int|None=None) -> Iterable[BucketHitTuple]: ...


class Reader(Protocol):
    def read(self, rec_ref) -> Reading: ...

class Writer(Protocol):
    def write(self, reading) -> Any: ...

class Accessor(Protocol):
    def read(self, rec_ref) -> Reading: ...
    def write(self, reading) -> Any: ...

class GreedyReading(Reading):
    def __init__(self):
        self.points: list[PointTuple] = []
        self.bucket_goals: list[BucketGoalTuple] = []
        self.axes: list[AxisTuple] = []
        self.axis_values: list[AxisValueTuple] = []
        self.goals: list[GoalTuple] = []
        self.point_hits: list[PointHitTuple] = []
        self.bucket_hits: list[BucketHitTuple] = []

    def get_def_sha(self) -> str: raise NotImplementedError
    def get_rec_sha(self) -> str: raise NotImplementedError

    def iter_points(self, start: int=0, end: int|None=None) -> Iterable[PointTuple]:
        yield from self.points[start: end]

    def iter_bucket_goals(self, start: int=0, end: int|None=None) -> Iterable[BucketGoalTuple]:
        yield from self.bucket_goals[start: end]

    def iter_axes(self, start: int=0, end: int|None=None) -> Iterable[AxisTuple]:
        yield from self.axes[start: end]

    def iter_axis_values(self, start: int=0, end: int|None=None) -> Iterable[AxisValueTuple]:
        yield from self.axis_values[start: end]

    def iter_goals(self, start: int=0, end: int|None=None) -> Iterable[GoalTuple]:
        yield from self.goals[start: end]

    def iter_point_hits(self, start: int=0, end: int|None=None) -> Iterable[PointHitTuple]:
        yield from self.point_hits[start: end]

    def iter_bucket_hits(self, start: int=0, end: int|None=None) -> Iterable[BucketHitTuple]:
        yield from self.bucket_hits[start: end]


