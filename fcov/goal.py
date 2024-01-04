# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

from dataclasses import dataclass


@dataclass
class GoalItem:  # Better name required
    name: str = "DEFAULT"
    amount: int = 10
    description: str = ""