from dataclasses import dataclass


@dataclass
class GoalItem:  # Better name required
    name: str = "DEFAULT"
    amount: int = 10
    description: str = ""