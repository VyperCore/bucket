

from typing import Iterable

from fcov.rw.base import BucketHitTuple, PointHitTuple
from .base import AxisTuple, AxisValueTuple, BucketGoalTuple, BucketHitTuple, GoalTuple, PointHitTuple, PointTuple, Reading


class MergeReading(Reading):

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

    def iter_points(self, start: int=0, end: int|None=None) -> Iterable[PointTuple]:
        yield from self.master.iter_points(start, end)

    def iter_bucket_goals(self, start: int=0, end: int|None=None) -> Iterable[BucketGoalTuple]:
        yield from self.master.iter_bucket_goals(start, end)

    def iter_axes(self, start: int=0, end: int|None=None) -> Iterable[AxisTuple]:
        yield from self.master.iter_axes(start, end)

    def iter_axis_values(self, start: int=0, end: int|None=None) -> Iterable[AxisValueTuple]:
        yield from self.master.iter_axis_values(start, end)

    def iter_goals(self, start: int=0, end: int|None=None) -> Iterable[GoalTuple]:
        yield from self.master.iter_goals(start, end)

    def iter_bucket_hits(self, start: int = 0, end: int | None = None) -> Iterable[BucketHitTuple]:
        for offset, hits in enumerate(self.bucket_hits[start: end]):
            yield BucketHitTuple(start+offset, hits)

    def iter_point_hits(self, start: int = 0, end: int | None = None) -> Iterable[PointHitTuple]:
        for point in self.iter_points(start, end):
            hits = 0
            hit_buckets = 0 
            full_buckets = 0 
            for bucket_hit in self.iter_bucket_hits(point.bucket_start, point.bucket_end):
                target = self.bucket_targets[bucket_hit.start]
                if target > 0:
                    bucket_hits = min(bucket_hit.hits, target)
                    if bucket_hit.hits > 0:
                        hit_buckets += 1
                        if bucket_hits == target:
                            full_buckets += 1
                        hits += bucket_hits

            yield PointHitTuple(start=point.start, depth=point.depth, hits=hits, hit_buckets=hit_buckets, full_buckets=full_buckets)

    def merge(self, *readings: Reading):
        master_def_sha = self.get_def_sha()
        master_rec_sha = self.get_rec_sha()

        for reading in readings:
            if reading.get_def_sha() != master_def_sha:
                raise RuntimeError("Tried to merge coverage with two different definition hashes!")
            
            if reading.get_rec_sha() != master_rec_sha:
                raise RuntimeError("Tried to merge coverage with two different record hashes!")

            for bucket_hit in reading.iter_bucket_hits():
                self.bucket_hits[bucket_hit.start] += bucket_hit.hits
