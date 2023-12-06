from dataclasses import dataclass
from .chain import OpenLink, Link

@dataclass
class GoalItem:  # Better name required
    name: str = "DEFAULT"
    target: int = 10
    description: str = ""

    def chain(self, start: OpenLink | None = None) -> Link:
        start = start or OpenLink(prev=None)
        return start.close(self, goal_size=1)
