# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from ..axis import Axis
from ..covergroup import CoverBase
from ..coverpoint import Coverpoint
from ..goal import GoalItem
from .common import (
    AxisTuple,
    AxisValueTuple,
    BucketGoalTuple,
    BucketHitTuple,
    GoalTuple,
    PointHitTuple,
    PointTuple,
    PuppetReading,
    Reader,
)


class PointReader(Reader):
    """
    Read coverage from coverpoints
    """

    def __init__(self, context_sha):
        self._rec_sha = context_sha

    def read(self, point):
        reading = PuppetReading()

        chain = point._chain_def()
        reading.def_sha = chain.end.sha.hexdigest()
        reading.rec_sha = self._rec_sha
        for point_link in sorted(
            chain.index.iter(CoverBase), key=lambda link: (link.start.point, link.depth)
        ):
            reading.points.append(PointTuple.from_link(point_link))

            if isinstance(point_link.item, Coverpoint):
                start = point_link.start.bucket
                goal_start = point_link.start.goal
                goal_offsets = {
                    k: i for i, k in enumerate(point_link.item._goal_dict.keys())
                }
                for offset, goal in enumerate(point_link.item._bucket_goals()):
                    bg_tuple = BucketGoalTuple(
                        start=(start + offset), goal=(goal_start + goal_offsets[goal])
                    )
                    reading.bucket_goals.append(bg_tuple)

        for axis_link in chain.index.iter(Axis):
            reading.axes.append(AxisTuple.from_link(axis_link))

            start = axis_link.start.axis_value
            for offset, axis_value in enumerate(axis_link.item.values.keys()):
                av_tuple = AxisValueTuple(start=(start + offset), value=axis_value)
                reading.axis_values.append(av_tuple)

        for goal_link in chain.index.iter(GoalItem):
            reading.goals.append(GoalTuple.from_link(goal_link))

        self.point = point
        chain = self.point._chain_run()

        for point_link in sorted(
            chain.index.iter(CoverBase), key=lambda link: (link.start.point, link.depth)
        ):
            reading.point_hits.append(PointHitTuple.from_link(point_link))

            if isinstance(point_link.item, Coverpoint):
                start = point_link.start.bucket
                for offset, hits in enumerate(point_link.item._bucket_hits()):
                    bh_tuple = BucketHitTuple(start=(start + offset), hits=hits)
                    reading.bucket_hits.append(bh_tuple)

        return reading
