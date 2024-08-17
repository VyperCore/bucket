# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from dataclasses import dataclass
import hashlib
from .common.chain import OpenLink, Link
from .link import CovDef, CovRun

@dataclass
class GoalItem:
    name: str = "DEFAULT"
    target: int = 10
    description: str = ""

    def __post_init__(self):
        self.sha = hashlib.sha256((self.name+self.description+str(self.target)).encode())

    def chain(self, start: OpenLink[CovDef] | None = None) -> Link[CovDef]:
        start = start or OpenLink(CovDef())
        link = CovDef(goal=1, sha=self.sha)
        return start.close(self, link=link, typ=GoalItem)
