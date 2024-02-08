# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

from git.repo import Repo
from bucket import CoverageContext, Covergroup, Coverpoint, Sampler, AxisUtils

from .rw import PointReader, SQLAccessor, MergeReading, ConsoleWriter

# This file contains useful reference code (such as example coverpoints,
# covergroups, etc), as well as some necessary code to get the example working. 

# Covergroups
class TopDogs(Covergroup):
    def setup(self, ctx):
        self.add_coverpoint(DogStats(name="doggy_stats", description="Some basic doggy stats"))
        self.add_covergroup(
            DogsAndToys(name="doggy_coverage", description="A group of coverpoints about dogs")
        )

class DogsAndToys(Covergroup):
    def setup(self, ctx):
        self.add_coverpoint(ChewToysByAge(name="chew_toys_by_age", description="Preferred chew toys by age"))
        self.add_coverpoint(
            ChewToysByName(name="chew_toys_by_name__group_a", description="Preferred chew toys by name - Group A", names=["Barbara", "Connie", "Graham"])
        )
        self.add_coverpoint(
            ChewToysByName(name="chew_toys_by_name__group_b", description="Preferred chew toys by name - Group B", names=["Clive", "Derek", "Ethel"])
        )

class DogStats(Coverpoint):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

    def setup(self, ctx):
        self.add_axis(
            name="name",
            values=["Clive", "Derek", "Ethel", "Barbara", "Connie", "Graham"],
            description="All the acceptable dog names",
        )
        self.add_axis(
            name="age",
            values=list(range(16)),
            description="Dog age in years",
        )
        self.add_axis(
            name="size",
            values={"Small": [0, 10], "medium": [11, 30], "large": [31, 50]},
            description="Rough size estimate from weight",
        )

        self.add_goal("HECKIN_CHONKY", -1, "Puppies can't be this big!")

    def apply_goals(self, bucket, goals):
        if int(bucket.age) <= 1 and bucket.size in ["large"]:
            return goals.HECKIN_CHONKY

    def sample(self, trace):
        # 'with cursor' is used, so cursor values are cleared each time
        # cursor can also be manaually cleared by using cursor.clear()
        with self.cursor as cursor:
            cursor.set_cursor(
                name=trace['Name'],
                age=trace['Age'],
                size=trace['Weight']
            )
            self.cursor.increment()

class ChewToysByAge(Coverpoint):
    def __init__(self, name: str, description: str):
        super().__init__(name, description)

    def setup(self, ctx):

        self.add_axis(
            name="breed",
            values={"Border Collie":[0,1], "Whippet":2, "Labrador":3, "Cockapoo":4},
            description="All known dog breeds"
        )
        self.add_axis(
            name="age",
            values=['Puppy', 'Adult', 'Senior'],
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
            description="This makes no sense to display as one_hot, but here we are"
        )

        self.add_goal("NO_SLIPPERS", -1, "Only puppies chew slippers!")
        self.add_goal("STICK", 50, "Yay sticks!")

    def apply_goals(self, bucket, goals):
        if bucket.age != "Puppy" and bucket.favourite_toy in ["slipper"]:
            return goals.NO_SLIPPERS
        elif bucket.favourite_toy == "stick":
            return goals.STICK

    def sample(self, trace):
        # 'with cursor' is used, so cursor values are cleared each time
        # cursor can also be manaually cleared by using cursor.clear()

        dog_age = trace['Age']
        if dog_age < 2:
            age = 'Puppy'
        elif dog_age > 12:
            age = 'Senior'
        else:
            age = 'Adult'

        with self.cursor as cursor:
            cursor.set_cursor(
                breed=trace['Breed'],
                age=age,
                favourite_leg=trace['Leg']
            )

            # For when multiple values might need covering from one trace
            # Only need to set the axes that change
            for toy in range(len(trace['Chew_toy'])):
                cursor.set_cursor(favourite_toy=trace['Chew_toy'][toy])
                cursor.increment()



class ChewToysByName(Coverpoint):
    def __init__(self, name: str, description: str, names):
        self.name_group = names
        super().__init__(name, description)

    def setup(self, ctx):
        self.add_axis(
            name="breed",
            values={"Border Collie":[0,1], "Whippet":2, "Labrador":3, "Cockapoo":4},
            description="All known dog breeds"
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

    def sample(self, trace):
        # 'with cursor' is used, so cursor values are cleared each time
        # cursor can also be manaually cleared by using cursor.clear()

        if trace['Name'] not in self.name_group:
            return
        
        with self.cursor as cursor:
            cursor.set_cursor(
                breed=trace['Breed'],
                name=trace['Name'],
            )

            # For when multiple values might need covering from one trace
            # Only need to set the axes that change
            for toy in range(len(trace['Chew_toy'])):
                cursor.set_cursor(favourite_toy=trace['Chew_toy'][toy])
                cursor.increment()


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
        # types of data as required.
        trace = {}
        trace['Breed'] = self.random.choice(["Border Collie", "Whippet", "Labrador", "Cockapoo", 0, 1, 2, 3, 4])
        trace['Chew_toy'] = self.random.choices(["Slipper", "Ball", "Stick", "Ring"], k=2)
        trace['Weight'] = self.random.randint(5, 50)
        trace['Age'] = self.random.randint(0, 15)
        trace['Name'] = self.random.choice(["Clive", "Derek", "Ethel", "Barbara", "Connie", "Graham"])
        trace['Leg'] = self.random.choice([1,2,4,8])

        return trace



if __name__ == "__main__":
    # testbench
    with CoverageContext(isa="THIS IS AN ISA"):
        cvg_a = TopDogs(name="Dogs", description="Doggy coverage")

    with CoverageContext(isa="THIS IS AN ISA"):
        cvg_b = TopDogs(name="Dogs", description="Doggy coverage")

    cvg_a.print_tree()
    cvg_a.doggy_coverage.print_tree()

    sampler = MySampler(coverage=cvg_a)
    for _ in range(100):
        sampler.sample(sampler.create_trace())

    sampler = MySampler(coverage=cvg_b)
    for _ in range(500):
        sampler.sample(sampler.create_trace())

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
    sql_accessor = SQLAccessor.File("example_file_store")

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
    print(f"To view this coverage in detail please run: python -m bucket read --sql-path example_file_store --points --record {rec_ref_a}")
    ConsoleWriter(axes=False, goals=False, points=False).write(reading_a)
    print("\nThis is the coverage from 2 regressions. One with 100 samples, and one with 500:")
    print(f"To view this coverage in detail please run: python -m bucket read --sql-path example_file_store --points --record {rec_ref_merged}")
    ConsoleWriter(axes=False, goals=False, points=False).write(merged_reading)

    # Read all back from sql - note as the db is not removed this will 
    # acumulate each time this example is run. This will also include
    # merged data as well as the individual runs. It is meant as an example
    # of how to use the command
    merged_reading_all = MergeReading(*sql_accessor.read_all())
    print("\nThis is the coverage from all the regression data so far:")
    print("(To reset please delete the file 'example_file_store')")
    ConsoleWriter(axes=False, goals=False, points=False).write(merged_reading_all)
