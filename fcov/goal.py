from dataclasses import dataclass
from .common.chain import OpenLink, Link
from .link import CovDef, CovRes

@dataclass
class GoalItem:  # Better name required
    name: str = "DEFAULT"
    target: int = 10
    description: str = ""

    def chain(self, start: OpenLink[CovDef] | None = None) -> Link[CovDef]:
        start = start or OpenLink(CovDef())
        link = CovDef(goal=1, target=self.target)
        return start.close(self, link=link, typ=GoalItem)
