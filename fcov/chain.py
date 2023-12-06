from dataclasses import field, dataclass, replace
from typing import TYPE_CHECKING, Iterable, Optional
if TYPE_CHECKING:
    from covergroup import CoverBase
    from axis import Axis
    from goal import GoalItem
    CoverItem = CoverBase | Axis | GoalItem

@dataclass(kw_only=True)
class OpenLink:
    prev: "Link | None" = field(repr=False)
    depth: int = 0
    point_start: int = 0
    axis_start: int = 0
    axis_value_start: int = 0
    goal_start: int = 0
    bucket_start: int = 0
    target_start: int = 0

    def link_down(self):
        return replace(self, prev=self.prev, depth=self.depth+1)

    def close(self, item: "CoverItem", child: Optional["Link"]=None, 
              point_size: int = 0,
              axis_size: int = 0,
              axis_value_size: int = 0,
              goal_size: int = 0,
              bucket_size: int = 0,
              target_size: int = 0
        ):
        start_data = self.__dict__
        if child is None:
            end_data = {
                "point_end": self.point_start + point_size,
                "axis_end": self.axis_start + axis_size,
                "axis_value_end": self.axis_value_start + axis_value_size,
                "goal_end": self.goal_start + goal_size,
                "bucket_end": self.bucket_start + bucket_size,
                "target_end": self.target_start + target_size,
            }
            prev = self.prev
            depth = self.depth
        else:
            end_data = {
                "point_end": child.point_end + point_size,
                "axis_end": child.axis_end + axis_size,
                "axis_value_end": child.axis_value_end + axis_value_size,
                "goal_end": child.goal_end + goal_size,
                "bucket_end": child.bucket_end + bucket_size,
                "target_end": child.target_end + target_size,
            }
            prev = child
            depth = child.depth - 1

        merge = {
            **end_data, 
            **start_data,
            "item": item,
            "prev": prev,
            "depth": depth,
        }
        return Link(**merge)

@dataclass(kw_only=True)
class Link(OpenLink):
    item: "CoverItem"
    point_end: int = 0
    axis_end: int = 0
    axis_value_end: int = 0
    goal_end: int = 0
    bucket_end: int = 0
    target_end: int = 0

    def link_across(self):
        return OpenLink(
            prev=self,
            depth=self.depth, 
            point_start=self.point_end, 
            axis_start=self.axis_end,
            axis_value_start=self.axis_value_end,
            goal_start=self.goal_end,
            bucket_start=self.bucket_end,
            target_start=self.target_end,
        )

    def iter(self, typ: type | tuple[type] | None = None) -> Iterable["Link"]:
        link = self
        while link:
            if typ is None or isinstance(link.item, typ):
                yield link
            link = link.prev
