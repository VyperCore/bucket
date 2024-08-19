# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

import hashlib
import itertools
from types import SimpleNamespace
from typing import TYPE_CHECKING, Iterable

from .common.chain import Link, OpenLink
from .context import CoverageContext
from .link import CovDef, CovRun

if TYPE_CHECKING:
    from .coverpoint import Coverpoint


class CoverBase:
    name: str
    description: str
    target: int
    hits: int

    def setup(self):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def sample(self, trace):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def _chain_def(self, start: OpenLink[CovDef] | None = None) -> Link[CovDef]: ...

    def _chain_run(self, start: OpenLink[CovRun] | None = None) -> Link[CovRun]: ...


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
        self.full_name = name.lower()

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
        self._set_full_name()

    def setup(self, ctx: SimpleNamespace):
        raise NotImplementedError("This needs to be implemented by the covergroup")

    def _set_full_name(self):
        """
        Set full_name strings for each child
        """
        for cp in self.coverpoints.values():
            cp.full_name = self.full_name + f".{cp.name.lower()}"

        for cg in self.covergroups.values():
            cg.full_name = self.full_name + f".{cg.name.lower()}"
            cg._set_full_name()

    def apply_filter(self, filter:dict|list|str):
        """
        Sanitise input then call _apply_filter recursively
        """
        if isinstance(filter, str):
            s_filter = {'allow': [filter]}
        elif isinstance(filter, list):
            s_filter = {'allow': filter}
        else:
            s_filter = filter
        
        assert isinstance(s_filter, dict)
        if 'allow' in s_filter:
            assert isinstance(s_filter['allow'], list), f"allow entries must be list[str]"
            for s in s_filter['allow']:
                assert isinstance(s, str), f"allow filter entries must be str"
            s_filter['allow'][:] = [x.lower() for x in s_filter['allow']]
        if 'deny' in s_filter:
            assert isinstance(s_filter['deny'], list), f"deny entries must be list[str]"
            for s in s_filter['allow']:
                assert isinstance(s, str), f"deny filter entries must be str"
            s_filter['deny'][:] = [x.lower() for x in s_filter['deny']]

        self._apply_filter(s_filter)

        return self


    def _apply_filter(self, filter:dict, allowed:bool=False, denied:bool=False):
        """
        Match against filter strings and recursively call _apply_filter
        """
        # See if covergroup is a match for allow/deny first, as could mean
        # children don't need to be checked

        # Filter for deny
        if denied:
            deny_match = True
        elif 'deny' in filter:
            if any(f_str in self.full_name for f_str in filter['deny']):
                deny_match = True
            else:
                deny_match = False
        else:
            deny_match = False

        # Filter for allow
        if allowed:
            allow_match = True
        elif 'allow' in filter and not deny_match:
            if any(f_str in self.full_name for f_str in filter['allow']):
                allow_match = True
            else:
                allow_match = False
        else:
            allow_match = True

        any_children_active = False
        for cp in self.coverpoints.values():
            any_children_active |= cp._apply_filter(filter, allowed=allow_match, denied=deny_match)

        for cg in self.covergroups.values():
            any_children_active |= cg._apply_filter(filter, allowed=allow_match, denied=deny_match)

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
