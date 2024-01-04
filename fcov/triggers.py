# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

from enum import Enum, auto


class CoverageTriggers(Enum):
    ALL = auto()
    SOMETIMES = auto()
    OCCASSIONALLY = auto()