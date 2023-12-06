from dataclasses import dataclass


@dataclass
class GoalItem:  # Better name required
    name: str = "DEFAULT"
    target: int = 10
    description: str = ""