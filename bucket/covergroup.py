# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

import hashlib
import itertools
from types import SimpleNamespace
from typing import Iterable

from .common.chain import Link, OpenLink
from .context import CoverageContext
from .link import CovDef, CovRun


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
            cvg_tier: what coverage tier is being run [0..3]
        """

        self.name = name
        self.description = description

        self.coverpoints = {}
        self.covergroups = {}
        self.sha = hashlib.sha256((self.name + self.description).encode())
        self.setup(ctx=CoverageContext.get())

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

    def setup(self, ctx: SimpleNamespace):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def print_tree(self, indent: int = 0):
        """Print out coverage hierarch from this covergroup down"""
        if indent == 0:
            print("COVERAGE_TREE")
            print(f"* {self.name}: {self.description}")
        indent += 1
        indentation = "    " * indent
        for cp in self.coverpoints.values():
            print(f"{indentation}|-- {cp.name}: {cp.description}")

        for cg in self.covergroups.values():
            print(f"{indentation}|-- {cg.name}: {cg.description}")
            cg.print_tree(indent + 1)

    def sample(self, trace):
        """Call sample on all sub-groups and coverpoints, passing in trace object"""
        for cp in self.coverpoints.values():
            cp.sample(trace)

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
