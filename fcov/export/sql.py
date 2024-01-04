# SPDX-License-Identifier: MIT
# Copyright (c) 2023 Vypercore. All Rights Reserved

from fcov.common.chain import Link
from ..link import CovDef, CovRun
from sqlalchemy import Integer, String, select, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from ..goal import GoalItem

from ..axis import Axis
from . import base

from ..covergroup import CoverBase, Covergroup
from ..coverpoint import Coverpoint
from rich.table import Table, Column
from rich.console import Console

class BaseRow(DeclarativeBase): ...

class DefinitionRow(BaseRow):
    __tablename__ = "definition"
    definition:       Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

class RunRow(BaseRow):
    __tablename__ = "run"
    run:              Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    definition:       Mapped[int] = mapped_column(Integer)

class PointRow(BaseRow):
    __tablename__ = "point"
    definition:       Mapped[int] = mapped_column(Integer, primary_key=True)
    start:            Mapped[int] = mapped_column(Integer, primary_key=True)
    depth:            Mapped[int] = mapped_column(Integer, primary_key=True)
    end:              Mapped[int] = mapped_column(Integer)
    axis_start:       Mapped[int] = mapped_column(Integer)
    axis_end:         Mapped[int] = mapped_column(Integer)
    axis_value_start: Mapped[int] = mapped_column(Integer)
    axis_value_end:   Mapped[int] = mapped_column(Integer)
    goal_start:       Mapped[int] = mapped_column(Integer)
    goal_end:         Mapped[int] = mapped_column(Integer)
    bucket_start:     Mapped[int] = mapped_column(Integer)
    bucket_end:       Mapped[int] = mapped_column(Integer)
    target:           Mapped[int] = mapped_column(Integer)
    target_buckets:   Mapped[int] = mapped_column(Integer)
    name:             Mapped[str] = mapped_column(String(30))
    description:      Mapped[str] = mapped_column(String(30))

    @classmethod
    def from_link(cls, definition: int, link: Link[CovDef]):
        return cls(definition=definition,
                   start=link.start.point,
                   end=link.end.point,
                   depth=link.depth,
                   axis_start=link.start.axis,
                   axis_end=link.end.axis,
                   axis_value_start=link.start.axis_value,
                   axis_value_end=link.end.axis_value,
                   goal_start=link.start.goal,
                   goal_end=link.end.goal,
                   bucket_start=link.start.bucket,
                   bucket_end=link.end.bucket,
                   target=link.end.target-link.start.target,
                   target_buckets=link.end.target_buckets-link.start.target_buckets,
                   name=link.item.name,
                   description=link.item.description
        )

class AxisRow(BaseRow):
    __tablename__ = "axis"
    definition:       Mapped[int] = mapped_column(Integer, primary_key=True)
    start:            Mapped[int] = mapped_column(Integer, primary_key=True)
    value_start:      Mapped[int] = mapped_column(Integer)
    value_end:        Mapped[int] = mapped_column(Integer)
    name:             Mapped[str] = mapped_column(String(30))
    description:      Mapped[str] = mapped_column(String(30))

    @classmethod
    def from_link(cls, definition: int, link: Link[CovDef]):
        return cls(definition=definition,
                   start=link.start.axis,
                   value_start=link.start.axis_value,
                   value_end=link.end.axis_value,
                   name=link.item.name,
                   description=link.item.description
        )

class GoalRow(BaseRow):
    __tablename__ = "goal"
    definition:       Mapped[int] = mapped_column(Integer, primary_key=True)
    start:            Mapped[int] = mapped_column(Integer, primary_key=True)
    target:           Mapped[int] = mapped_column(Integer)
    name:             Mapped[str] = mapped_column(String(30))
    description:      Mapped[str] = mapped_column(String(30))

    @classmethod
    def from_link(cls, definition: int, link: Link[CovDef]):
        return cls(definition=definition,
                   start=link.start.goal,
                   target=link.end.target-link.start.target,
                   name=link.item.name,
                   description=link.item.description
        )

class AxisValueRow(BaseRow):
    __tablename__ = "axis_value"
    definition:           Mapped[int] = mapped_column(Integer, primary_key=True)
    start:            Mapped[int] = mapped_column(Integer, primary_key=True)
    value:            Mapped[str] = mapped_column(String(30))

    @classmethod
    def from_axis_value(cls, definition: int, start: int, axis_value: str):
        return cls(definition=definition, start=start, value=axis_value)

class BucketGoalRow(BaseRow):
    __tablename__ = "bucket_goal"
    definition:       Mapped[int] = mapped_column(Integer, primary_key=True)
    start:            Mapped[int] = mapped_column(Integer, primary_key=True)
    goal:             Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_bucket_goal(cls, definition: int, start: int, goal: int):
        return cls(definition=definition, start=start, goal=goal)


class PointHitRow(BaseRow):
    __tablename__ = "point_hit"
    run:              Mapped[int] = mapped_column(Integer, primary_key=True)
    start:            Mapped[int] = mapped_column(Integer, primary_key=True)
    depth:            Mapped[int] = mapped_column(Integer, primary_key=True)
    hits:             Mapped[int] = mapped_column(Integer)
    hit_buckets:      Mapped[int] = mapped_column(Integer)
    full_buckets:     Mapped[int] = mapped_column(Integer)
    
    @classmethod
    def from_link(cls, run: int, link: Link[CovRun]):
        return cls(run=run,
                   start=link.start.point,
                   depth=link.depth,
                   hits=link.end.hits-link.start.hits,
                   hit_buckets=link.end.hit_buckets-link.start.hit_buckets,
                   full_buckets=link.end.full_buckets-link.start.full_buckets,
        )


class BucketHitRow(BaseRow):
    __tablename__ = "bucket_hit"
    run:              Mapped[int] = mapped_column(Integer, primary_key=True)
    start:            Mapped[int] = mapped_column(Integer, primary_key=True)
    hits:             Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_bucket_hits(cls, run: int, start: int, hits: int):
        return cls(run=run, start=start, hits=hits)

class Exporter(base.Exporter[int, int]):
    def __init__(self):
        self.engine = create_engine("sqlite://", echo=True)
        BaseRow.metadata.create_all(self.engine)

    def write_def(self, chain: Link[CovDef]) -> int:
        with Session(self.engine) as session:
            # Insert a source row first
            def_row = DefinitionRow()
            session.add(def_row)
            session.commit()
            definition = def_row.definition

            for point_link in chain.index.iter(Covergroup):
                session.add(PointRow.from_link(definition, point_link))

            for point_link in chain.index.iter(Coverpoint):
                session.add(PointRow.from_link(definition, point_link))

                start = point_link.start.bucket
                goal_start = point_link.start.goal
                goal_offsets = {k:i for i,k in enumerate(point_link.item._goal_dict.keys())}
                for offset, goal in enumerate(point_link.item.bucket_goals()):
                    session.add(BucketGoalRow.from_bucket_goal(definition, start + offset, goal_start + goal_offsets[goal]))

            for axis_link in chain.index.iter(Axis):
                session.add(AxisRow.from_link(definition, axis_link))

                start = axis_link.start.axis_value
                for offset, axis_value in enumerate(axis_link.item.values.keys()):
                    session.add(AxisValueRow.from_axis_value(definition, start + offset, axis_value))

            for goal_link in chain.index.iter(GoalItem):
                session.add(GoalRow.from_link(definition, goal_link))

            session.commit()
        
        return definition

    def write_run(self, definition: int, chain: Link[CovRun]) -> int:
            
        with Session(self.engine) as session:
            # Insert a source row first
            run_row = RunRow(definition=definition)
            session.add(run_row)
            session.commit()
            run = run_row.run

            for point_link in chain.index.iter(Covergroup):
                session.add(PointHitRow.from_link(run, point_link))

            for point_link in chain.index.iter(Coverpoint):
                session.add(PointHitRow.from_link(run, point_link))

                start = point_link.start.bucket
                for offset, hits in enumerate(point_link.item.bucket_hits()):
                    session.add(BucketHitRow.from_bucket_hits(run, start + offset, hits))
            
            session.commit()

        return run

    def read_run(self, run: int):
        with Session(self.engine) as session:
            run_row = session.scalars(select(RunRow).where(RunRow.run==run)).one()
            definition = run_row.definition

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

            point_st = select(PointRow).where(PointRow.definition==definition).order_by(PointRow.start, PointRow.depth)
            point_hit_st = select(PointHitRow).where(PointHitRow.run==run).order_by(PointHitRow.start, PointHitRow.depth)

            axis_st = select(AxisRow).where(AxisRow.definition==definition).order_by(AxisRow.start)
            axis_value_st = select(AxisValueRow).where(AxisValueRow.definition==definition).order_by(AxisValueRow.start)
            goal_st = select(GoalRow).where(GoalRow.definition==definition).order_by(GoalRow.start)

            bucket_goal_st = select(BucketGoalRow).where(BucketGoalRow.definition==definition).order_by(BucketGoalRow.start)
            bucket_hit_st = select(BucketHitRow).where(BucketHitRow.run==run).order_by(BucketHitRow.start)

            point_rows = session.scalars(point_st).all()
            point_hit_rows = session.scalars(point_hit_st).all()

            axis_rows = session.scalars(axis_st).all()
            axis_value_rows = session.scalars(axis_value_st).all()
            goal_rows = session.scalars(goal_st).all()

            bucket_goal_rows = session.scalars(bucket_goal_st).all()
            bucket_hit_rows = session.scalars(bucket_hit_st).all()

            for point, point_hit in zip(point_rows, point_hit_rows):
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

                summary_table.add_row(name, desc, 
                                      str(target), str(hits), f"{target_percent:.2f}%",
                                      str(bucket_target), str(bucket_hits), str(buckets_full), 
                                      f"{bucket_target_percent:.2f}%", f"{buckets_full_percent:.2f}%")

                if point.end != point.start + 1:
                    # It's a cover group
                    continue

                axis_table = Table("Name", "Description", title=f"{point.name} - Axes")
                point_tables.append(axis_table)

                axis_offset_sizes = []
                axis_titles = []
                for axis in axis_rows[point.axis_start: point.axis_end]:
                    axis_offset_sizes.append((axis.value_start, axis.value_end-axis.value_start))
                    axis_table.add_row(axis.name, axis.description)
                    axis_titles.append(axis.name)

                goal_table = Table("Name", "Description", "Target", title=f"{point.name} - Goals")
                point_tables.append(goal_table)
                for goal in goal_rows[point.goal_start: point.goal_end]:
                    goal_table.add_row(goal.name, goal.description, str(goal.target))

                point_table = Table(*(axis_titles + point_table_base_columns), title=f"{point.name} - {point.description}")
                point_tables.append(point_table)

                point_bucket_goals = bucket_goal_rows[point.bucket_start: point.bucket_end]
                point_bucket_hits = bucket_hit_rows[point.bucket_start: point.bucket_end]

                for bucket_goal, bucket_hit in zip(point_bucket_goals, point_bucket_hits):
                    goal = goal_rows[bucket_goal.goal]
                    hits = bucket_hit.hits
                    target = goal.target

                    if target > 0:
                        target_percent = f"{(min(target,hits) / target) * 100:.2f}%"
                    else:
                        target_percent = "-"

                    bucket_columns = []

                    offset = (bucket_goal.start - point.bucket_start)
                    for (axis_offset, axis_size) in axis_offset_sizes:
                        bucket_columns.append(axis_value_rows[axis_offset + (offset % axis_size)].value)
                        offset //= axis_size

                    bucket_columns += [str(hits), str(target), target_percent, goal.name, goal.description]

                    point_table.add_row(*bucket_columns)

            console = Console()
            for point_table in point_tables:
                console.print(point_table)
            console.print(summary_table)

