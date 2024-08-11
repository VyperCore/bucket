# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from git.repo import Repo

from bucket import AxisUtils, CoverageContext, Covergroup, Coverpoint, Sampler

from .rw import ConsoleWriter, MergeReading, PointReader, SQLAccessor

# This file contains useful reference code (such as example coverpoints,
# covergroups, etc), as well as some necessary code to get the example working
# outside of a full testbench.


# Covergroups
class TopDogs(Covergroup):
    """
    This covergroup is top level covergroup, containing all other covergroups/coverpoints.
    An instance of this covergroup will be passed to the sampler.
    """

    def setup(self, ctx):
        self.add_coverpoint(
            DogStats(name="doggy_stats", description="Some basic doggy stats")
        )
        self.add_covergroup(
            DogsAndToys(
                name="chew_toys",
                description="A group of coverpoints about dog chew toys",
            )
        )


class DogsAndToys(Covergroup):
    """
    This is another covergroup to group similar coverpoints together.
    """

    def setup(self, ctx):
        self.add_coverpoint(
            ChewToysByAge(
                name="chew_toys_by_age", description="Preferred chew toys by age"
            )
        )
        self.add_coverpoint(
            ChewToysByName(
                name="chew_toys_by_name__group_a",
                description="Preferred chew toys by name - Group A",
                names=["Barbara", "Connie", "Graham"],
            )
        )
        self.add_coverpoint(
            ChewToysByName(
                name="chew_toys_by_name__group_b",
                description="Preferred chew toys by name - Group B",
                names=["Clive", "Derek", "Ethel"],
            )
        )


class DogStats(Coverpoint):
    """
    This is an example coverpoint with 3 axes, each demonstrating a different way of
    specifying values to the axis.
    """

    def __init__(self, name: str, description: str):
        super().__init__(name, description)

    def setup(self, ctx):
        # The values passed to this axis are a simple list of str
        self.add_axis(
            name="name",
            values=["Clive", "Derek", "Ethel", "Barbara", "Connie", "Graham"],
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
            name="size",
            values={"Small": [0, 10], "medium": [11, 30], "large": [31, 50]},
            description="Rough size estimate from weight",
        )

        # Here we create a new goal, defined as ILLEGAL
        # If a bucket with this goal applied is hit, when an error will be generated
        self.add_goal("HECKIN_CHONKY", "Puppies can't be this big!", illegal=True)

    def apply_goals(self, bucket, goals):
        # Buckets use str names, not values. If you want to compare against a value,
        # you must first convert the string back to int, etc
        # Any bucket with no goal assigned, will have the default goal applied
        if int(bucket.age) <= 1 and bucket.size in ["large"]:
            return goals.HECKIN_CHONKY

    def sample(self, trace):
        self.bucket.clear()
        self.bucket.set_axes(name=trace["Name"], age=trace["Age"], size=trace["Weight"])
        self.bucket.hit()


class ChewToysByAge(Coverpoint):
    """
    This is another example coverpoint. This one contains an axis demonstrating the use of
    common axis values provided as part of this library (eg. msb, one_hot)
    """

    def __init__(self, name: str, description: str):
        super().__init__(name, description)

    def setup(self, ctx):
        self.add_axis(
            name="breed",
            values={
                "Border Collie": [0, 1],
                "Whippet": 2,
                "Labrador": 3,
                "Cockapoo": 4,
            },
            description="All known dog breeds",
        )
        self.add_axis(
            name="age",
            values=["Puppy", "Adult", "Senior"],
            description="Range of dog years",
        )
        self.add_axis(
            name="favourite_toy",
            values=["Slipper", "Ball", "Stick", "Ring"],
            description="Types of dog toys",
        )

        self.add_axis(
            name="favourite_leg",
            values=AxisUtils.one_hot(width=4),
            description="This makes no sense to display as one_hot, but here we are",
        )

        self.add_goal("NO_SLIPPERS", "Only puppies chew slippers!", illegal=True)
        self.add_goal(
            "FRONT_LEGS_ONLY",
            "Only care about seniors who pick their favourite front legs",
            ignore=True,
        )
        self.add_goal("STICK", "Yay sticks!", target=50)

    def apply_goals(self, bucket, goals):
        # Apply goal if any dog which is not a puppy likes slippers
        if bucket.age != "Puppy" and bucket.favourite_toy in ["Slipper"]:
            return goals.NO_SLIPPERS
        # Apply goal for senior dogs who chose a favourite back leg
        elif bucket.age == "Senior" and int(bucket.favourite_leg, base=0) & 0x3:
            return goals.FRONT_LEGS_ONLY
        # Apply goal for any time a dog picks stick (if above goals don't apply)
        elif bucket.favourite_toy == "Stick":
            return goals.STICK
        # Else default goal will be used

    def sample(self, trace):
        # 'with bucket' is used, so bucket values are cleared each time
        # bucket can also be manually cleared by using bucket.clear()

        # This could also be achieved by creating the axis with
        # a dict which specifies ranges for each age group. Then the value
        # from trace can be set directly without processing here.
        dog_age = trace["Age"]
        if dog_age < 2:
            age = "Puppy"
        elif dog_age > 12:
            age = "Senior"
        else:
            age = "Adult"

        with self.bucket as bucket:
            bucket.set_axes(breed=trace["Breed"], age=age, favourite_leg=trace["Leg"])

            # For when multiple values might need covering from one trace
            # Only need to set the axes that change
            for toy in range(len(trace["Chew_toy"])):
                bucket.set_axes(favourite_toy=trace["Chew_toy"][toy])
                bucket.hit()


class ChewToysByName(Coverpoint):
    def __init__(self, name: str, description: str, names):
        self.name_group = names
        super().__init__(name, description)

    def setup(self, ctx):
        self.add_axis(
            name="breed",
            values={
                "Border Collie": [0, 1],
                "Whippet": 2,
                "Labrador": 3,
                "Cockapoo": 4,
            },
            description="All known dog breeds",
        )
        self.add_axis(
            name="name",
            values=self.name_group,
            description="Most important dog names only",
        )
        self.add_axis(
            name="favourite_toy",
            values=["Slipper", "Ball", "Stick", "Ring"],
            description="Types of dog toys",
        )

        self.add_goal("WEIRDO_DOG", "Dogs named Barbara can't be trusted", ignore=True)

    def apply_goals(self, bucket, goals):
        if bucket.breed == "Border Collie" and bucket.name in ["Barbara"]:
            return goals.WEIRDO_DOG

    def sample(self, trace):
        # 'with bucket' is used, so bucket values are cleared each time
        # bucket can also be manually cleared by using bucket.clear()

        if trace["Name"] not in self.name_group:
            return

        with self.bucket as bucket:
            bucket.set_axes(
                breed=trace["Breed"],
                name=trace["Name"],
            )

            # For when multiple values might need covering from one trace
            # Only need to set the axes that change
            for toy in range(len(trace["Chew_toy"])):
                bucket.set_axes(favourite_toy=trace["Chew_toy"][toy])
                bucket.hit()


# Sampler
class MySampler(Sampler):
    def __init__(self, coverage):
        super().__init__(coverage=coverage)

        import random

        self.random = random.Random()

    def create_trace(self):
        """Nonsense function"""
        # This should come from monitors, etc
        # For this example, create random doggy data and put in a dictionary
        # In practise this would normally be a class, which can be populated with many
        # types of data as required.
        trace = {}
        trace["Breed"] = self.random.choice(
            ["Border Collie", "Whippet", "Labrador", "Cockapoo", 0, 1, 2, 3, 4]
        )
        trace["Chew_toy"] = self.random.choices(
            ["Slipper", "Ball", "Stick", "Ring"], k=2
        )
        trace["Weight"] = self.random.randint(5, 50)
        trace["Age"] = self.random.randint(0, 15)
        trace["Name"] = self.random.choice(
            ["Clive", "Derek", "Ethel", "Barbara", "Connie", "Graham"]
        )
        trace["Leg"] = self.random.choice([1, 2, 4, 8])

        return trace


if __name__ == "__main__":
    # Instance two copies of the coverage. Normally only one is required, but this is to
    # demonstrate merging coverage.
    with CoverageContext(isa="THIS IS AN ISA"):
        cvg_a = TopDogs(name="Dogs", description="Doggy coverage").include_by_name(
            "toys_by_name"
        )
        cvg_a.exclude_by_name(["group_b"])

    with CoverageContext(isa="THIS IS AN ISA"):
        cvg_b = TopDogs(name="Dogs", description="Doggy coverage")

    # Instance 2 samplers. Again, you would only normally have one, but two are used here
    # to demonstrate merging coverage from multiple regressions/tests.
    sampler_a = MySampler(coverage=cvg_a)
    for _ in range(100):
        sampler_a.sample(sampler_a.create_trace())

    sampler_b = MySampler(coverage=cvg_b)
    for _ in range(500):
        sampler_b.sample(sampler_b.create_trace())

    # Create a context specific hash
    # This is stored alongside recorded coverage and is used to determine if
    # coverage is valid to merge.
    context_hash = Repo().head.object.hexsha

    # Create a reader
    point_reader = PointReader(context_hash)

    # Read the two sets of coverage
    reading_a = point_reader.read(cvg_a)
    reading_b = point_reader.read(cvg_b)

    # Create a local sql database
    sql_accessor = SQLAccessor.File("example_file_store.db")

    # Write each reading into the database
    rec_ref_a = sql_accessor.write(reading_a)
    rec_ref_b = sql_accessor.write(reading_b)

    # Read back from sql
    sql_reading_a = sql_accessor.read(rec_ref_a)
    sql_reading_b = sql_accessor.read(rec_ref_b)

    # Merge together
    merged_reading = MergeReading(sql_reading_a, sql_reading_b)

    # Write merged coverage into the database
    rec_ref_merged = sql_accessor.write(merged_reading)

    # Output to console
    print("\n-------------------------------------------------------")
    print("This is the coverage with 100 samples:")
    print(
        f"To view this coverage in detail please run: python -m bucket read --sql-path example_file_store --points --record {rec_ref_a}"
    )
    ConsoleWriter(axes=False, goals=False, points=False).write(reading_a)
    print(
        "\nThis is the coverage from 2 regressions. One with 100 samples, and one with 500:"
    )
    print(
        f"To view this coverage in detail please run: python -m bucket read --sql-path example_file_store --points --record {rec_ref_merged}"
    )
    ConsoleWriter(axes=False, goals=False, points=False).write(merged_reading)

    # Read all back from sql - note as the db is not removed this will
    # acumulate each time this example is run. This will also include
    # merged data as well as the individual runs. It is meant as an example
    # of how to use the command
    merged_reading_all = MergeReading(*sql_accessor.read_all())
    print("\nThis is the coverage from all the regression data so far:")
    print("(To reset please delete the file 'example_file_store')")
    ConsoleWriter(axes=False, goals=False, points=False).write(merged_reading_all)

    # print_tree() is a useful function to see the hierarchy of your coverage
    # You can call it from the top level covergroup, or from another covergroup
    # within your coverage tree.
    cvg_a.print_tree()
    cvg_a.chew_toys.print_tree()
