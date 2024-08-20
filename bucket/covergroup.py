# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

import hashlib
import itertools
from types import SimpleNamespace
from typing import TYPE_CHECKING, Callable, Iterable

from pydantic import validate_call

from .base import CoverBase
from .common.chain import Link, OpenLink
from .common.types import MatchStrs, TagStrs
from .context import CoverageContext
from .link import CovDef, CovRun

if TYPE_CHECKING:
    from .coverpoint import Coverpoint


class Covergroup(CoverBase):
    """This class groups coverpoints together, and adds them to the hierarchy"""

    @validate_call
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

        self.tier = None
        self.tags = []

        self._filter_applied = False
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
        self._update_tags_and_tiers()

    def setup(self, ctx: SimpleNamespace):
        raise NotImplementedError("This needs to be implemented by the covergroup")

    def _update_tags_and_tiers(self):
        """
        Update covergroup with child tiers and tags
        """
        for child in self.iter_children():
            if self.tier is None or child.tier < self.tier:
                self.tier = child.tier
            for tag in child.tags:
                if tag not in self.tags:
                    self.tags.append(tag)

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
    def include_by_function(self, matcher: Callable[[CoverBase], bool]):
        """
        Enable coverpoints which match the provided function. Unmatched coverpoints will not have their active state changed, except this is the first filter to be applied, then any coverpoints which do not match are explicitly set to inactive, as the default state is active.
        Parameters:
            matcher: A function to match against coverpoint/covergroup data
        """
        mismatch_state = None
        if not self._filter_applied:
            mismatch_state = False
        self._apply_filter(matcher, True, mismatch_state)
        return self

    @validate_call
    def restrict_by_function(self, matcher: Callable[[CoverBase], bool]):
        """
        Filter coverpoints which match the provided function. Those that match will not change their active state, those that don't match will be set to inactive.
        Parameters:
            matcher: A function to match against coverpoint/covergroup data
        """
        self._apply_filter(matcher, None, False)
        return self

    @validate_call
    def exclude_by_function(self, matcher: Callable[[CoverBase], bool]):
        """
        Disable coverpoints which match the provided function. Unmatched coverpoints will not have their active state changed.
        Parameters:
            matcher: A function to match against coverpoint/covergroup data
        """
        self._apply_filter(matcher, False, None)
        return self

    @validate_call
    def include_by_name(self, names: MatchStrs):
        """
        Enable coverpoints which match the provided names. Unmatched coverpoints will not have their active state changed, except this is the first filter to be applied, then any coverpoints which do not match are explicitly set to inactive, as the default state is active.
        Parameters:
            names: A case-insensitive string or string list to match against
        """
        return self.include_by_function(self._match_by_name(names))

    @validate_call
    def restrict_by_name(self, names: MatchStrs):
        """
        Filter coverpoints which match the provided names. Those that match will not change their active state, those that don't match will be set to inactive.
        Parameters:
            names: A case-insensitive string or string list to match against
        """
        return self.exclude_by_function(self._match_by_name(names))

    @validate_call
    def exclude_by_name(self, names: MatchStrs):
        """
        Disable coverpoints which match the provided names. Unmatched coverpoints will not have their active state changed.
        Parameters:
            names: A case-insensitive string or string list to match against
        """
        return self.exclude_by_function(self._match_by_name(names))

    @validate_call
    def set_tier_level(self, tier: int):
        """
        Filter the coverage tree for coverpoints equal to or less than 'tier'. Those that match will not change their active state, those that don't match will be set to inactive.
        Parameters:
            tier: The highest tier to be set active
        """
        return self.restrict_by_function(self._match_by_tier(tier))

    @validate_call
    def include_by_tags(self, tags: TagStrs, match_all: bool = False):
        """
        Enable coverpoints which match the provided tags. Unmatched coverpoints will not have their active state changed, except this is the first filter to be applied, then any coverpoints which do not match are explicitly set to inactive, as the default state is active.
        Parameters:
            tags: Tag(s) to match against
            match_all: If set, all tags must match. If cleared, any tags can match (default: False)
        """
        return self.include_by_function(self._match_by_tags(tags, match_all))

    @validate_call
    def restrict_by_tags(self, tags: TagStrs, match_all: bool = False):
        """
        Filter coverpoints which match the provided tags. Those that match will not change their active state, those that don't match will be set to inactive.
        Parameters:
            tags: Tag(s) to match against
            match_all: If set, all tags must match. If cleared, any tags can match
        """
        return self.exclude_by_function(self._match_by_tags(tags))

    @validate_call
    def exclude_by_tags(self, tags: TagStrs, match_all: bool = False):
        """
        Disable coverpoints which match the provided tags. Unmatched coverpoints will not have their active state changed.
        Parameters:
            tags: Tag(s) to match against
            match_all: If set, all tags must match. If cleared, any tags can match
        """
        return self.exclude_by_function(self._match_by_tags(tags))

    def _match_by_name(self, names: MatchStrs):
        def matcher(cp: CoverBase):
            l_name = cp.full_path.lower()
            return any(f_str in l_name for f_str in names)

        return matcher

    def _match_by_tier(self, tier: int):
        def matcher(cp: CoverBase):
            return cp.tier <= tier

        return matcher

    def _match_by_tags(self, tags: TagStrs, match_all: bool = False):
        def matcher(cp: CoverBase):
            if match_all:
                for tag in tags:
                    if tag not in cp.tags:
                        return False
                return True
            else:
                for tag in tags:
                    if tag in cp.tags:
                        return True
                return False

        return matcher

    def _apply_filter(
        self,
        matcher: Callable[[CoverBase], bool],
        match_state: bool | None,
        mismatch_state: bool | None,
    ):
        self._filter_applied = True
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
        """
        if coverpoint.name in self.coverpoints:
            raise Exception("Coverpoint names must be unique within a covergroup")
        coverpoint.parent = self
        self.coverpoints[coverpoint.name] = coverpoint

    def add_covergroup(self, covergroup: "Covergroup"):
        """
        Add a covergroup instance to the covergroup
        Parameters:
            covergroup: instance of a covergroup
        """
        if covergroup.name in self.covergroups:
            raise Exception("Covergroup names must be unique within a covergroup")
        covergroup.parent = self
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

    @validate_call
    def print_tree(self, indent: int = 0):
        """Print out coverage hierarch from this covergroup down"""

        def fmt_active(active):
            return "A" if active else "-"

        if indent == 0:
            print("COVERAGE_TREE")
            print(
                f"[{fmt_active(self.active)}]({self.tier}) {self.name}: {self.description} -- Tags:{self.tags}"
            )
        indent += 1
        indentation = "    " * indent
        for cp in self.coverpoints.values():
            print(
                f"[{fmt_active(cp.active)}]({cp.tier}) {indentation}|-- {cp.name}: {cp.description} -- Tags:{cp.tags}"
            )

        for cg in self.covergroups.values():
            print(
                f"[{fmt_active(cg.active)}]({cg.tier}) {indentation}|-- {cg.name}: {cg.description} -- Tags:{cg.tags}"
            )
            cg.print_tree(indent + 1)

    def sample(self, trace):
        """Pass trace to sample on all sub-groups and coverpoints, if active"""
        if self.active:
            for cp in self.coverpoints.values():
                cp._sample(trace)

            for cg in self.covergroups.values():
                cg.sample(trace)

    @validate_call
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
