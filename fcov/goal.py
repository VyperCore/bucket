from dataclasses import dataclass


@dataclass
class GoalItem:  # Better name required
    name: str = "DEFAULT"
    target: int = 10
    description: str = ""
    _offset = None

    def identify(self, offset: int):
        self._offset = offset

    @classmethod
    def field_keys(cls):
        return ("target", "name", "description")

    def field_values(self):
        return (self.target, self.name, self.description)
