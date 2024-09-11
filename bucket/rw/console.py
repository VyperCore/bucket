# SPDX-License-Identifier: MIT
# Copyright (c) 2023-2024 Vypercore. All Rights Reserved

from rich.console import Console
from rich.table import Column, Table

from .common import Reading, Writer


class ConsoleWriter(Writer):
    """
    Write coverage information out to the terminal using Rich.
    """

    def __init__(self, axes=False, goals=False, points=False, summary=True):
        self.write_axes = axes
        self.write_goals = goals
        self.write_points = points
        self.write_summary = summary

    def write(self, reading: Reading):
        summary_table_columns = [
            Column("Name", justify="left", style="cyan", no_wrap=True),
            Column("Description", justify="left", style="cyan", no_wrap=True),
            Column("Target", justify="right", style="cyan", no_wrap=True),
            Column("Hits", justify="right", style="cyan", no_wrap=True),
            Column("Hits %", justify="right", style="cyan", no_wrap=True),
            Column("Target Buckets", justify="right", style="cyan", no_wrap=True),
            Column("Hit Buckets", justify="right", style="cyan", no_wrap=True),
            Column("Full Buckets", justify="right", style="cyan", no_wrap=True),
            Column("Hit %", justify="right", style="cyan", no_wrap=True),
            Column("Full %", justify="right", style="cyan", no_wrap=True),
        ]
        summary_table = Table(*summary_table_columns, title="Point Summary")

        point_tables = []
        point_table_base_columns = [
            Column("Hits", justify="right", style="cyan", no_wrap=True),
            Column("Target", justify="right", style="cyan", no_wrap=True),
            Column("Target %", justify="right", style="cyan", no_wrap=True),
            Column("Goal Name", justify="left", style="cyan", no_wrap=True),
            Column("Goal Description", justify="left", style="cyan", no_wrap=True),
        ]

        goals = list(reading.iter_goals())
        axis_values = list(reading.iter_axis_values())

        for point, point_hit in zip(reading.iter_points(), reading.iter_point_hits()):
            name = f"{point.depth * '| '}{point.name}"
            desc = point.description
            hits = point_hit.hits
            target = point.target
            target_percent = (hits / target) * 100

            bucket_hits = point_hit.hit_buckets
            bucket_target = point.target_buckets
            bucket_target_percent = (bucket_hits / bucket_target) * 100

            buckets_full = point_hit.full_buckets
            buckets_full_percent = (buckets_full / bucket_target) * 100

            summary_table.add_row(
                name,
                desc,
                str(target),
                str(hits),
                f"{target_percent:.2f}%",
                str(bucket_target),
                str(bucket_hits),
                str(buckets_full),
                f"{bucket_target_percent:.2f}%",
                f"{buckets_full_percent:.2f}%",
            )

            if point.end != point.start + 1:
                # It's a cover group
                continue

            axis_table = Table("Name", "Description", title=f"{point.name} - Axes")
            if self.write_axes:
                point_tables.append(axis_table)

            axis_offset_sizes = []
            axis_titles = []
            for axis in reading.iter_axes(point.axis_start, point.axis_end):
                axis_offset_sizes.append(
                    (axis.value_start, axis.value_end - axis.value_start)
                )
                axis_table.add_row(axis.name, axis.description)
                axis_titles.append(axis.name)
            axis_offset_sizes.reverse()

            if self.write_goals:
                goal_table = Table(
                    "Name", "Description", "Target", title=f"{point.name} - Goals"
                )
                point_tables.append(goal_table)
                for goal in reading.iter_goals(point.goal_start, point.goal_end):
                    goal_table.add_row(goal.name, goal.description, str(goal.target))

            if self.write_points:
                standard_columns = [c.copy() for c in point_table_base_columns]
                point_table = Table(
                    *(axis_titles + standard_columns),
                    title=f"{point.name} - {point.description}",
                )
                point_tables.append(point_table)

                point_bucket_goals = reading.iter_bucket_goals(
                    point.bucket_start, point.bucket_end
                )
                point_bucket_hits = reading.iter_bucket_hits(
                    point.bucket_start, point.bucket_end
                )
                for bucket_goal, bucket_hit in zip(
                    point_bucket_goals, point_bucket_hits
                ):
                    goal = goals[bucket_goal.goal]

                    target = goal.target

                    if target > 0:
                        hits = bucket_hit.hits
                        target_percent = f"{(min(target,hits) / target) * 100:.2f}%"
                    else:
                        if hits != 0:
                            print(
                                f"Expect hits to be zero for ignore/illegal buckets, got {hits}"
                            )
                        hits = "-"
                        target_percent = "-"

                    bucket_columns = []

                    # Find the offset of the bucket within the coverpoint
                    offset = bucket_goal.start - point.bucket_start

                    # We're now getting the axis values from the bucket index.
                    #
                    # The axis values are in a flat list ordered by axis:
                    #
                    #   axis_value | axis  value_in_axis
                    #   0          | 0     0
                    #   1          | 0     1
                    #   2          | 0     2
                    #   3          | 1     0
                    #   4          | 1     1
                    #
                    # The buckets are in a flat list ordered by axis combination, such that the last
                    # axis changes most frequently.
                    #
                    #   bucket | axis_0 axis_1
                    #   0      | 0      0
                    #   1      | 0      1
                    #   2      | 1      0
                    #   3      | 1      1
                    #   4      | 2      0
                    #   5      | 2      1
                    #
                    # To find the axis value for each axis from the bucket, we go through the axes
                    # from last to first, finding the axis position and size within the axis values,
                    # and the bucket index offset within each axis. # The '%' and '//=' operators here
                    # are used to align the offset within the values for an axis.
                    for axis_offset, axis_size in axis_offset_sizes:
                        bucket_columns.insert(
                            0, axis_values[axis_offset + (offset % axis_size)].value
                        )
                        offset //= axis_size

                    bucket_columns += [
                        str(hits),
                        str(target),
                        target_percent,
                        goal.name,
                        goal.description,
                    ]
                    point_table.add_row(*bucket_columns)

        console = Console()
        for point_table in point_tables:
            console.print(point_table)
        if self.write_summary:
            console.print(summary_table)
