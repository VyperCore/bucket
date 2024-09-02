# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from bucket import Covergroup, Coverpoint

# This file contains useful reference code (such as example coverpoints,
# covergroups, etc), as well as some necessary code to get the example working
# outside of a full testbench.


# Covergroups
class TopCats(Covergroup):
    """
    This covergroup contains all cat related coverage.
    """

    def setup(self, ctx):
        self.add_coverpoint(
            CatStats(name="cat_stats", description="Some basic cat stats")
            .set_tier(1)
            .set_tags(["basic", "stats"])
        )
        self.add_covergroup(
            CatsAndToys(
                name="play_toys",
                description="A group of coverpoints about cat play toys",
            )
        )

    def should_sample(self, trace):
        """
        This function is used to stop cat coverage being sampled when not relevant
        """
        return True if trace["type"] == "Cat" else False


class CatsAndToys(Covergroup):
    """
    This is another covergroup to group similar coverpoints together.
    """

    def setup(self, ctx):
        self.add_coverpoint(
            PlayToysByAge(
                name="play_toys_by_age",
                description="Preferred play toys by age",
            )
        )

        # Split names into groups, then assign to coverpoints
        name_groups = {"A-C": [], "D-F": [], "Other": []}
        for name in ctx.pet_info.pet_names:
            if name < "D":
                name_groups["A-C"].append(name)
            elif name < "G":
                name_groups["D-F"].append(name)
            else:
                name_groups["Other"].append(name)

        for idx, group in enumerate(name_groups.keys()):
            self.add_coverpoint(
                PlayToysByName(
                    name=f"play_toys_by_name__group_{idx}",
                    description=f"Preferred play toys by name (Group {idx})",
                    names=name_groups[group],
                )
            )


class CatStats(Coverpoint):
    """
    This is an example coverpoint with 3 axes, each demonstrating a different way of
    specifying values to the axis.
    """

    def __init__(self, name: str, description: str):
        # Shortlist of names we care about
        self.important_names = [
            "Clive",
            "Derek",
            "Ethel",
            "Barbara",
            "Connie",
            "Graham",
        ]

        # NOTE: Any variables in self should be added BEFORE calling super.init
        # as this will call setup

        super().__init__(name, description)

    def setup(self, ctx):
        # The values passed to this axis are a simple list of str
        self.add_axis(
            name="name",
            values=self.important_names,
            description="All the acceptable dog names",
        )
        # The values passed to this axes is a list of int
        self.add_axis(
            name="age",
            values=list(range(16)),
            description="Dog age in years",
        )
        # The values in this axis are named ranges, in a dict.
        # Single values and ranges can be mixed in a dict
        self.add_axis(
            name="evil_thoughts",
            values={"low": [0, 10], "medium": [11, 30], "high (normal)": [31, 50]},
            description="Number of evil thoughts per day",
        )

        # Here we create a new goal, defined as ILLEGAL
        # If a bucket with this goal applied is hit, when an error will be generated
        self.add_goal(
            "SUSPICIOUS",
            "Old cats are quite evil and need to be seen more often!",
            target=100,
        )

    def apply_goals(self, bucket, goals):
        # Buckets use str names, not values. If you want to compare against a value,
        # you must first convert the string back to int, etc
        # Any bucket with no goal assigned, will have the default goal applied
        if int(bucket.age) >= 13 and bucket.evil_thoughts in ["low"]:
            return goals.SUSPICIOUS

    def sample(self, trace):
        if trace["Name"] not in self.important_names:
            return

        self.bucket.clear()
        self.bucket.set_axes(
            name=trace["Name"], age=trace["Age"], evil_thoughts=trace["Evil_thoughts"]
        )
        self.bucket.hit()


class PlayToysByAge(Coverpoint):
    """
    This is another example coverpoint. This one contains an axis demonstrating the use of
    common axis values provided as part of this library (eg. msb, one_hot)
    """

    def __init__(self, name: str, description: str):
        super().__init__(name, description)

    def setup(self, ctx):
        self.add_axis(
            name="breed",
            values=ctx.pet_info.cat_breeds,
            description="All known cat breeds",
        )
        self.add_axis(
            name="age",
            values=["Kitten", "Adult", "Senior"],
            description="Range of cat years",
        )
        self.add_axis(
            name="favourite_toy",
            values=["Toy_mouse", "Scratching Post", "Laser", "Box"],
            description="Types of cat toys",
        )

        self.add_goal("BOX", "Cats love boxes!", target=150)

    def apply_goals(self, bucket, goals):
        # Apply goal for any time a cat picks box
        if bucket.favourite_toy == "Box":
            return goals.BOX
        # Else default goal will be used

    def sample(self, trace):
        # 'with bucket' is used, so bucket values are cleared each time
        # bucket can also be manually cleared by using bucket.clear()

        # This could also be achieved by creating the axis with
        # a dict which specifies ranges for each age group. Then the value
        # from trace can be set directly without processing here.
        cat_age = trace["Age"]
        if cat_age < 2:
            age = "Kitten"
        elif cat_age > 12:
            age = "Senior"
        else:
            age = "Adult"

        with self.bucket as bucket:
            bucket.set_axes(breed=trace["Breed"], age=age)
            bucket.set_axes(favourite_toy=trace["Play_toy"])
            bucket.hit()


class PlayToysByName(Coverpoint):
    def __init__(self, name: str, description: str, names):
        self.valid_names = names
        super().__init__(name, description)

    def setup(self, ctx):
        self.add_axis(
            name="breed",
            values=ctx.pet_info.cat_breeds,
            description="All known cat breeds",
        )
        self.add_axis(
            name="name",
            values=self.valid_names,
            description="Most important cat names only",
        )
        self.add_axis(
            name="favourite_toy",
            values=["Toy_mouse", "Scratching Post", "Laser", "Box"],
            description="Types of cat toys",
        )

    def sample(self, trace):
        # 'with bucket' is used, so bucket values are cleared each time
        # bucket can also be manually cleared by using bucket.clear()
        if trace["Name"] not in self.valid_names:
            return

        with self.bucket as bucket:
            bucket.set_axes(
                breed=trace["Breed"],
                name=trace["Name"],
                favourite_toy=trace["Play_toy"],
            )
            bucket.hit()
