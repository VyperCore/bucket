# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

from functools import lru_cache


class Axis:
    def __init__(self, name, values, description):
        self.name = name
        self.values = self.sanitise_values(values)
        self.description = description

        print(f"Added {self.name}: {self.description}. Values are {self.values}")

    def sanitise_values(self, values):
        # Take input values and return a dict
        # Input values can be in the form of dict, tuple, list or set
        # The return dictionary will have string form of the values as the key
        # and the values (or ranges) as the value.
        if isinstance(values, dict):
            values_dict = values
        elif isinstance(values, list | tuple | set):
            values_dict = {}
            for v in values:
                if isinstance(v, list | tuple | set):
                    assert len(v) == 2, f"length of min-max is not 2. Length was {len(v)}: ({v})"
                    sorted_v = sorted(v)
                    key = f"{sorted_v[0]} -> {sorted_v[1]}"
                    values_dict[key] = sorted_v
                else:
                    values_dict[str(v)] = v
        else:
            raise Exception(
                f"Unexpected type for values. Got {type(values)}, exp dict/list/tuple/set"
            )

        for key in values_dict:
            assert isinstance(
                key, str
            ), f'Values provided for axis "{self.name}" \
                are incorrectly formatted: {values}'

        return values_dict

    @lru_cache(maxsize=128)  # noqa: B019
    def get_named_value(self, value):
        if (value_str := str(value)) in self.values:
            return value_str
        else:
            # Must be named or in a range
            for k, v in self.values.items():
                if value == v:
                    return k
                elif isinstance(v, list):
                    if v[0] <= value <= v[1]:
                        return k
            raise Exception(f"Unrecognised value for axis '{self.name}': {value}")