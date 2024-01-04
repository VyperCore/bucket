# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

from dataclasses import dataclass, fields
from typing import Self

@dataclass(kw_only=True)
class CovDef:
    point: int = 0
    axis: int = 0
    axis_value: int = 0
    goal: int = 0
    bucket: int = 0
    target: int = 0
    target_buckets: int = 0

    def __add__(self, other: Self) -> Self:
        new = type(self)()
        for field in fields(self):
            setattr(new, field.name, getattr(self, field.name) + getattr(other, field.name))
        return new

@dataclass(kw_only=True)
class CovRes:
    point: int = 0
    bucket: int = 0
    hits: int = 0
    hit_buckets: int = 0
    full_buckets: int = 0

    def __add__(self, other: Self) -> Self:
        new = type(self)()
        for field in fields(self):
            setattr(new, field.name, getattr(self, field.name) + getattr(other, field.name))
        return new
