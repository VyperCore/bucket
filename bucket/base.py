# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from typing import Callable

from .common.chain import Link, OpenLink
from .link import CovDef, CovRun


class CoverBase:
    name: str
    full_path: str
    description: str
    target: int
    hits: int

    def setup(self):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def sample(self, trace):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def _chain_def(self, start: OpenLink[CovDef] | None = None) -> Link[CovDef]: ...

    def _chain_run(self, start: OpenLink[CovRun] | None = None) -> Link[CovRun]: ...

    def _apply_filter(
        self,
        matcher: Callable[["CoverBase"], bool],
        match_state: bool,
        mismatch_state: bool | None,
    ) -> bool: ...
