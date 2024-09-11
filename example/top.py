# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from bucket import CoverTop, Sampler

from .cats import TopCats
from .dogs import TopDogs


# Top covergroup
class TopPets(CoverTop):
    """
    This covergroup is top level covergroup, containing all other covergroups/coverpoints.
    An instance of this covergroup will be passed to the sampler.
    """

    NAME = "Pets"
    DESCRIPTION = "Pet coverage"

    def setup(self, ctx):
        self.add_covergroup(TopDogs())
        self.add_covergroup(TopCats())


# Sampler
class MySampler(Sampler):
    def __init__(self, coverage):
        super().__init__(coverage=coverage)

        import random

        self.random = random.Random()

    def create_trace(self):
        """Nonsense function"""
        # This should come from monitors, etc
        # For this example, create random dog and cat data and put in a dictionary
        # In practise this would normally be a class, which can be populated with as
        # many types of nested data as required.
        trace = {}

        trace["type"] = self.random.choice(["Cat", "Dog"])
        trace["Breed"] = self.random.randint(0, 4)
        trace["Age"] = self.random.randint(0, 15)
        trace["Name"] = self.random.choice(MadeUpStuff.pet_names)

        if trace["type"] == "Dog":
            trace["Chew_toy"] = self.random.choices(
                ["Slipper", "Ball", "Stick", "Ring"], k=2
            )
            trace["Weight"] = self.random.randint(5, 50)
            trace["Leg"] = self.random.choice([1, 2, 4, 8])

        else:
            trace["Evil_thoughts"] = self.random.randint(5, 50)
            trace["Superiority"] = self.random.choice(["low", "medium", "high"])
            trace["Play_toy"] = self.random.choice(
                ["Toy_mouse", "Scratching Post", "Laser", "Box"]
            )
        return trace


class MadeUpStuff:
    # Example pet info to pass into coverage.
    # In real life, this would likely be a machine readable ISA, etc
    pet_names = [
        "Clive",
        "Derek",
        "Ethel",
        "Barbara",
        "Connie",
        "Graham",
        "Edward",
        "Stuart",
        "Peter",
    ]

    dog_breeds = {
        "Border Collie": [0, 1],
        "Whippet": 2,
        "Cockapoo": 3,
        "Golden Retriever": 4,
    }

    cat_breeds = {"Bengal": 0, "Burmese": 1, "Maine Coon": 2, "Persian": 3, "Nyan": 4}
