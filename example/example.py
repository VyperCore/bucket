# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from pathlib import Path

from git.repo import Repo

from bucket import CoverageContext
from bucket.rw import ConsoleWriter, HTMLWriter, MergeReading, PointReader, SQLAccessor

from .top import MadeUpStuff, MySampler, TopPets

# This file sets up and runs the example coverage. While it doesn't reflect the expected
# setup within a testbench, it will demonstrate several useful features.


def run(db_path: Path):
    # Get some common pet info for coverpoints to use
    pet_info = MadeUpStuff()

    # Instance two copies of the coverage. Normally only one is required, but this is to
    # demonstrate merging coverage.
    # The first instance demonstrates the use of filters to remove some of the coverage,
    # while still being able to merge with another run of coverage. These wouldn't
    # normally be hardcoded, but instead come from the command line/regression
    # configuration.
    with CoverageContext(pet_info=pet_info):
        cvg_a = TopPets(name="Pets", description="Pet coverage").include_by_name(
            "toys_by_name"
        )
        cvg_a.exclude_by_name(["group_b"])

    with CoverageContext(pet_info=pet_info):
        cvg_b = TopPets(name="Pets", description="Pet coverage")

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
    sql_accessor = SQLAccessor.File(db_path)

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
    # accumulate each time this example is run. This will also include
    # merged data as well as the individual runs. It is meant as an example
    # of how to use the command
    merged_reading_all = MergeReading(*sql_accessor.read_all())
    print("\nThis is the coverage from all the regression data so far:")
    print("(To reset please delete the file 'example_file_store')")
    ConsoleWriter(axes=False, goals=False, points=False).write(merged_reading_all)

    # Generating web viewer
    # To generate the HTML report run:
    # python -m bucket write html --sql-path ./example_file_store.db --output index.html
    HTMLWriter(
        web_path=Path(__file__).parent.parent / "viewer", output="index.html"
    ).write(merged_reading_all)

    print("\n-------------------------------------------------------")
    print("Open index.html to view coverage")

    # print_tree() is a useful function to see the hierarchy of your coverage
    # You can call it from the top level covergroup, or from another covergroup
    # within your coverage tree.
    print("\n-------------------------------------------------------")
    print("Print coverage tree for cvg_a")
    cvg_a.print_tree()
    cvg_a.dogs.print_tree()


if __name__ == "__main__":
    run("example_file_store.db")
