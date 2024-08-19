# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

import hashlib
import itertools
from types import SimpleNamespace
from typing import TYPE_CHECKING, Annotated, Callable, Iterable

from pydantic import AfterValidator, validate_call

from .common.chain import Link, OpenLink
from .context import CoverageContext
from .link import CovDef, CovRun

if TYPE_CHECKING:
    from .coverpoint import Coverpoint


def match_str_validator(m_strs: str | list[str]) -> list[str]:
    "Accept a str or list of strings and make them lowercase"
    if isinstance(m_strs, str):
        m_strs = [m_strs]
    m_strs[:] = (m_str.lower() for m_str in m_strs)
    return m_strs


MatchStrs = Annotated[str | list[str], AfterValidator(match_str_validator)]


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


class Covergroup(CoverBase):
    """This class groups coverpoints together, and adds them to the hierarchy"""

    def __init__(self, name: str, description: str):
        """
        Parameters:
            name: Name of covergroup
            description: Description of covergroup
        """

        self.name = name
        self.description = description
        # Required for top covergroup - will be overwritten for all others
        self.full_path = name.lower()

        self.active = True
        self.coverpoints = {}
        self.covergroups = {}
        self.sha = hashlib.sha256((self.name + self.description).encode())
        self._setup()

    def _setup(self):
        """
        This calls the user defined setup() plus any other setup required
        """
        self.setup(ctx=CoverageContext.get())
        self._set_full_path()

    def setup(self, ctx: SimpleNamespace):
        raise NotImplementedError("This needs to be implemented by the covergroup")

    def _set_full_path(self):
        """
        Set full_path strings for each child
        """
        for cp in self.coverpoints.values():
            cp.full_path = self.full_path + f".{cp.name.lower()}"

        for cg in self.covergroups.values():
            cg.full_path = self.full_path + f".{cg.name.lower()}"
            cg._set_full_path()

    @validate_call
    def include_by_name(self, names: MatchStrs, override: bool = True):
        """
        Filter the coverage tree, including only subtree which match `names`.
        Parameters:
            names: A case-insensitve string or string list to match against
            override: Whether to modify state of unmatched nodes (default true)
        """

        def matcher(cp: CoverBase):
            l_name = cp.full_path.lower()
            return any(f_str in l_name for f_str in names)

        self._apply_filter(matcher, True, False if override else None)

        return self

    @validate_call
    def exclude_by_name(self, names: MatchStrs, override: bool = False):
        """
        Filter the coverage tree, excluding subtrees which match `names`.
        Parameters:
            names: A case-insensitve string or string list to match against
            override: Whether to modify state of unmatched nodes (default false)
        """

        def matcher(cp: CoverBase):
            l_name = cp.full_path.lower()
            return any(f_str in l_name for f_str in names)

        self._apply_filter(matcher, False, True if override else None)

        return self

    def filter_by_function(
        self,
        matcher: Callable[[CoverBase], bool],
        match_state: bool,
        mismatch_state: bool | None,
    ):
        self._apply_filter(matcher, match_state, mismatch_state)
        return self

    def _apply_filter(
        self,
        matcher: Callable[[CoverBase], bool],
        match_state: bool,
        mismatch_state: bool | None,
    ):
        any_children_active = False
        if matcher(self):
            for child in self.iter_children():
                any_children_active |= child._apply_filter(
                    lambda _: True, match_state, mismatch_state
                )
        else:
            for child in self.iter_children():
                any_children_active |= child._apply_filter(
                    matcher, match_state, mismatch_state
                )

        self.active = any_children_active
        return self.active

    def add_coverpoint(self, coverpoint: "Coverpoint"):
        """
        Add a coverpoint instance to the covergroup
        Parameters:
            coverpoint: instance of a coverpoint
            trigger:    [optional] specific trigger on which to sample the coverpoint
        """
        if coverpoint.name in self.coverpoints:
            raise Exception("Coverpoint names must be unique within a covergroup")

        self.coverpoints[coverpoint.name] = coverpoint

    def add_covergroup(self, covergroup: "Covergroup"):
        """
        Add a covergroup instance to the covergroup
        Parameters:
            covergroup: instance of a covergroup
        """
        if covergroup.name in self.covergroups:
            raise Exception("Covergroup names must be unique within a covergroup")

        self.covergroups[covergroup.name] = covergroup

    def __getattr__(self, key: str):
        """
        Allow reference to child covergroups and coverpoints using <parent>.<child>
        """
        if key in self.covergroups:
            return self.covergroups[key]
        elif key in self.coverpoints:
            return self.coverpoints[key]
        else:
            return super().__getattribute__(key)

    def print_tree(self, indent: int = 0):
        """Print out coverage hierarch from this covergroup down"""
        if indent == 0:
            print("COVERAGE_TREE")
            print(f"* {self.name}: {self.description}")
        indent += 1
        indentation = "    " * indent
        for cp in self.coverpoints.values():
            active = "X" if cp.active else "-"
            print(f"[{active}] {indentation}|-- {cp.name}: {cp.description}")

        for cg in self.covergroups.values():
            active = "X" if cg.active else "-"
            print(f"[{active}] {indentation}|-- {cg.name}: {cg.description}")
            cg.print_tree(indent + 1)

    def sample(self, trace):
        """Pass trace to sample on all sub-groups and coverpoints, if active"""
        if self.active:
            for cp in self.coverpoints.values():
                cp._sample(trace)

            for cg in self.covergroups.values():
                cg.sample(trace)

    def iter_children(self) -> Iterable[CoverBase]:
        self.coverpoints = dict(sorted(self.coverpoints.items()))
        self.covergroups = dict(sorted(self.covergroups.items()))

        yield from itertools.chain(self.coverpoints.values(), self.covergroups.values())

    def _chain_def(self, start: OpenLink[CovDef] | None = None) -> Link[CovDef]:
        start = start or OpenLink(CovDef())
        child_start = start.link_down()
        child_close = None
        for child in self.iter_children():
            child_close = child._chain_def(child_start)
            child_start = child_close.link_across()
        return start.close(
            self, child=child_close, link=CovDef(point=1, sha=self.sha), typ=CoverBase
        )

    def _chain_run(self, start: OpenLink[CovRun] | None = None) -> Link[CovRun]:
        start = start or OpenLink(CovRun())
        child_start = start.link_down()
        child_close = None
        for child in self.iter_children():
            child_close = child._chain_run(child_start)
            child_start = child_close.link_across()
        return start.close(self, child=child_close, link=CovRun(point=1), typ=CoverBase)
