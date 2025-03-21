# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2025 Vypercore. All Rights Reserved

import pytest

from bucket.axis import Axis


class TestSanitiseValues:
    def test_dict_values(self):
        """Check that a unordered dict is returned as a sorted dict"""
        axis = Axis(name="test", values=[0], description="test")

        test_stimulus = {
            "Cherry": 3,
            "Banana": 2,
            "Apple": 1,
        }
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["Apple", "Banana", "Cherry"]
        assert list(result.values()) == [1, 2, 3]

    def test_list_values(self):
        """Check that a unordered list is returned as a sorted dict"""
        axis = Axis(name="test", values=[0], description="test")

        test_stimulus = [
            "Cherry",
            "Banana",
            "Apple",
        ]
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["Apple", "Banana", "Cherry"]
        assert list(result.values()) == ["Apple", "Banana", "Cherry"]

    def test_set_values(self):
        """Check that a unordered tuple is returned as a sorted dict"""
        axis = Axis(name="test", values=[0], description="test")

        test_stimulus = {
            "Cherry",
            "Banana",
            "Apple",
            "Banana",
        }
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["Apple", "Banana", "Cherry"]
        assert list(result.values()) == ["Apple", "Banana", "Cherry"]

    def test_tuple_values(self):
        """Check that a unordered tuple is returned as a sorted dict"""
        axis = Axis(name="test", values=[0], description="test")

        test_stimulus = (
            "Cherry",
            "Banana",
            "Apple",
        )
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["Apple", "Banana", "Cherry"]
        assert list(result.values()) == ["Apple", "Banana", "Cherry"]

    def test_default_other(self):
        """
        Other has been enabled, so should have an additional entry to catch unnamed values.
        """
        axis = Axis(name="test", values=[0], description="test", enable_other=True)

        test_stimulus = {
            "Cherry": 3,
            "Banana": 2,
            "Apple": 1,
        }
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["Apple", "Banana", "Cherry", "Other"]
        assert list(result.values()) == [1, 2, 3, None]

    def test_named_other(self):
        """
        Other has been enabled with a custom name, so should have an additional entry to catch
        unnamed values.
        """
        axis = Axis(
            name="test", values=[0], description="test", enable_other="Alternate Fruit"
        )

        test_stimulus = {
            "Cherry": 3,
            "Banana": 2,
            "Apple": 1,
        }
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["Alternate Fruit", "Apple", "Banana", "Cherry"]
        assert list(result.values()) == [None, 1, 2, 3]

    def test_named_other_clash(self):
        """
        Other has been enabled with a custom name which clashes.
        Should raise an assertion error.
        """
        axis = Axis(name="test", values=[0], description="test", enable_other="Apple")

        test_stimulus = {
            "Cherry": 3,
            "Banana": 2,
            "Apple": 1,
        }
        with pytest.raises(AssertionError, match='Values already contains "Apple"'):
            axis.sanitise_values(test_stimulus)

    def test_named_other_non_string(self):
        """
        Other has been enabled with a custom non-string name
        Should default to "Other"
        """
        axis = Axis(name="test", values=[0], description="test", enable_other=4)

        test_stimulus = {
            "Cherry": 3,
            "Banana": 2,
            "Apple": 1,
        }
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["Apple", "Banana", "Cherry", "Other"]
        assert list(result.values()) == [1, 2, 3, None]

    def test_undersized_set_range(self):
        """
        Pass in a set range with too few values
        Should raise an assertion error.
        """
        axis = Axis(
            name="test",
            values=[0],
            description="test",
        )

        test_stimulus = [1, 2, 3, 4, {5}]
        with pytest.raises(
            AssertionError, match="length of range is not 2. Length was 1"
        ):
            axis.sanitise_values(test_stimulus)

    def test_oversized_list_range(self):
        """
        Pass in a list range with too many values
        Should raise an assertion error.
        """
        axis = Axis(
            name="test",
            values=[0],
            description="test",
        )

        test_stimulus = [1, 2, 3, 4, [5, 6, 7]]
        with pytest.raises(
            AssertionError, match="length of range is not 2. Length was 3"
        ):
            axis.sanitise_values(test_stimulus)

    def test_non_int_tuple_range(self):
        """
        Pass in a tuple range with non-ints
        Should raise an assertion error.
        """
        axis = Axis(
            name="test",
            values=[0],
            description="test",
        )

        test_stimulus = [1, 2, 3, 4, ("Steve", "Bob")]
        with pytest.raises(
            AssertionError, match="Ranges should be specified as integers"
        ):
            axis.sanitise_values(test_stimulus)

    def test_dict_with_undersized_range(self):
        """
        Pass in a list range with non-ints, as part of dict
        Should raise an assertion error.
        """
        axis = Axis(
            name="test",
            values=[0],
            description="test",
        )

        test_stimulus = {"Apple": 1, "Banana": 2, "Cherry": [3]}
        with pytest.raises(
            AssertionError, match="length of range is not 2. Length was 1"
        ):
            axis.sanitise_values(test_stimulus)

    def test_dict_with_oversized_range(self):
        """
        Pass in a list range with non-ints, as part of dict
        Should raise an assertion error.
        """
        axis = Axis(
            name="test",
            values=[0],
            description="test",
        )

        test_stimulus = {"Apple": 1, "Banana": 2, "Cherry": [50, 63, 75, 88]}
        with pytest.raises(
            AssertionError, match="length of range is not 2. Length was 4"
        ):
            axis.sanitise_values(test_stimulus)

    def test_dict_with_non_int_range(self):
        """
        Pass in a tuple range with non-ints, as part of dict
        Should raise an assertion error.
        """
        axis = Axis(
            name="test",
            values=[0],
            description="test",
        )

        test_stimulus = {"Apple": 1, "Banana": 2, "Cherry": ("Steve", "Bob")}
        with pytest.raises(
            AssertionError, match="Ranges should be specified as integers"
        ):
            axis.sanitise_values(test_stimulus)

    def test_set_range_values(self):
        """Check that a unordered list is returned as a sorted dict"""
        axis = Axis(name="test", values=[0], description="test")

        test_stimulus = ["Cherry", "Banana", "Apple", {9, 3}]
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["3 -> 9", "Apple", "Banana", "Cherry"]
        assert list(result.values()) == [[3, 9], "Apple", "Banana", "Cherry"]

    def test_list_range_values(self):
        """Check that a unordered list is returned as a sorted dict"""
        axis = Axis(name="test", values=[0], description="test")

        test_stimulus = ["Cherry", "Banana", "Apple", [19, 5]]
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["5 -> 19", "Apple", "Banana", "Cherry"]
        assert list(result.values()) == [[5, 19], "Apple", "Banana", "Cherry"]

    def test_tuple_range_values(self):
        """Check that a unordered list is returned as a sorted dict"""
        axis = Axis(name="test", values=[0], description="test")

        test_stimulus = ["Cherry", "Banana", "Apple", (6, 1)]
        result = axis.sanitise_values(test_stimulus)
        assert list(result.keys()) == ["1 -> 6", "Apple", "Banana", "Cherry"]
        assert list(result.values()) == [[1, 6], "Apple", "Banana", "Cherry"]
