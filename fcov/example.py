from .context import CoverageContext
from .covergroup import Covergroup
from .coverpoint import Coverpoint
from .sampler import Sampler

# TODO
# - dump coverage at end of test into YAML
# - register triggers (default every clock cycle)
# - register cvg tier: only instance when required
# - present YAML in usable way
# - Trace struct, with setting functions
# - Optimise code


# def floatTrigger(trace):
#     return True if trace else false


# coverage
class MyCoverpoint(Coverpoint):
    def __init__(self, name: str, description: str, trigger=None):
        super().__init__(name, description, trigger=None)

    def setup(self, ctx):
        self.add_axis(
            name="my_axis_1",
            values=[0, 1, [2, 3]],
            description="Range of values for my_axis_1",
        )
        self.add_axis(
            name="my_axis_2",
            values=[6, 7, 8, 9],
            description="Range of values for my_axis_2",
        )
        self.add_axis(
            name="my_axis_3",
            values={"red": 0, "blue": 1, "green": [2, 3], "yellow": 4},
            description="Range of values for my_axis_3",
        )

        # def add_goals(self):
        self.add_goal("MOULDY_CHEESE", -1, "Not so gouda!")
        self.add_goal("OPTMISTIC_CHEESE", 20, "I brie-live in myself!")

    def apply_goals(self, bucket, goals):
        if bucket.my_axis_1 == "1" and bucket.my_axis_3 in ["red", "yellow"]:
            return goals.MOULDY_CHEESE
        elif int(bucket.my_axis_2) > 8:
            return goals.OPTMISTIC_CHEESE

    def sample(self, trace):
        # with cursor is used, so cursor values are cleared each time
        # cursor can also be manaually cleared by using cursor.clear()
        with self.cursor as cursor:
            cursor.set_cursor(
                my_axis_1=trace[0],
                my_axis_2=trace[1],
            )

            # For when multiple values might need covering from one trace
            # Only need to set the axes that change
            for colour in range(len(trace[2])):
                cursor.set_cursor(my_axis_3=trace[2][colour])
                cursor.increment()


# covergroups
class MyCovergroup(Covergroup):
    def setup(self, ctx):
        self.add_coverpoint(MyCoverpoint(name="my_coverpoint", description="A lovely coverpoint"))
        self.add_coverpoint(
            MyCoverpoint(name="another_coverpoint", description="A rather spiffing coverpoint")
        )


class MyBigCoverGroup(Covergroup):
    def setup(self, ctx):
        self.add_covergroup(
            MyCovergroup(name="my_covergroup", description="A group of coverpoints")
        )
        self.add_coverpoint(MyCoverpoint(name="some_coverpoint", description="A meh coverpoint"))


# Sampler
class MySampler(Sampler):
    def __init__(self, coverage):
        super().__init__(coverage=coverage)

        import random

        self.random = random.Random(2023)


    def create_trace(self):
        """Nonsense function"""
        # This should come from monitors, etc
        trace_data_1 = self.random.randint(0, 3)
        trace_data_2 = self.random.randint(6, 9)
        trace_data_3 = self.random.choices(["red", "green", "yellow", "blue", 0, 1, 2, 3, 4], k=2)

        data = (trace_data_1, trace_data_2, trace_data_3)
        print(f"TRACE_DATA: {data}")
        return data



if __name__ == "__main__":
    # testbench
    with CoverageContext(isa="THIS IS AN ISA"):
        cvg = MyBigCoverGroup(name="my_big_covergroup", description="A group of stuff")

    cvg.print_tree()
    cvg.my_covergroup.print_tree()

    sampler = MySampler(coverage=cvg)

    for _ in range(200):
        sampler.sample(sampler.create_trace())

    cvg.export_coverage()