from typing import Any, Protocol, TypeVar, Generic

from ..link import CovDef, CovRun
from ..common.chain import Link

DEF_T = TypeVar("DEF_T")
RUN_T = TypeVar("RUN_T")
class Exporter(Protocol[DEF_T, RUN_T]):

    def write_def(self, link: Link[CovDef]) -> DEF_T: ...
    def write_run(self, definition: DEF_T, link: Link[CovRun]) -> RUN_T: ...
    def read_run(self, run: RUN_T): ...

