from .base import Reader, GreedyReading, PointTuple, BucketGoalTuple, AxisTuple, AxisValueTuple, GoalTuple, BucketHitTuple, PointHitTuple
from ..covergroup import CoverBase, Covergroup
from ..coverpoint import Coverpoint
from ..goal import GoalItem
from ..axis import Axis

class PointReader(Reader, GreedyReading):
    def __init__(self, context_sha):
        GreedyReading.__init__(self)
        self._ref_sha = context_sha
    
    def get_def_sha(self):
        return self._def_sha

    def get_rec_sha(self):
        return self._ref_sha

    def read(self, point):
        chain = point.chain_def()
        self._def_sha = chain.end.sha.hexdigest()
        for point_link in sorted(chain.index.iter(CoverBase), key=lambda l:(l.start.point,l.depth)):
            self.points.append(PointTuple.from_link(point_link))

            if isinstance(point_link.item, Coverpoint):
                start = point_link.start.bucket
                goal_start = point_link.start.goal
                goal_offsets = {k:i for i,k in enumerate(point_link.item._goal_dict.keys())}
                for offset, goal in enumerate(point_link.item.bucket_goals()):
                    bg_tuple = BucketGoalTuple(start=(start+offset), goal=(goal_start+goal_offsets[goal]))
                    self.bucket_goals.append(bg_tuple)
    
        for axis_link in chain.index.iter(Axis):
            self.axes.append(AxisTuple.from_link(axis_link))

            start = axis_link.start.axis_value
            for offset, axis_value in enumerate(axis_link.item.values.keys()):
                av_tuple = AxisValueTuple(start=(start+offset), value=axis_value)
                self.axis_values.append(av_tuple)

        for goal_link in chain.index.iter(GoalItem):
            self.goals.append(GoalTuple.from_link(goal_link))

        self.point = point
        chain = self.point.chain_run()

        for point_link in sorted(chain.index.iter(CoverBase), key=lambda l:(l.start.point,l.depth)):
            self.point_hits.append(PointHitTuple.from_link(point_link))
            
            if isinstance(point_link.item, Coverpoint):
                start = point_link.start.bucket
                for offset, hits in enumerate(point_link.item.bucket_hits()):
                    bh_tuple = BucketHitTuple(start=(start+offset), hits=hits)
                    self.bucket_hits.append(bh_tuple)

        return self
