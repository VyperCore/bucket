
from fcov.chain import Link
from sqlalchemy import Integer, String, select, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from ..goal import GoalItem

from ..axis import Axis

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
    name:             Mapped[str] = mapped_column(String(30))
    description:      Mapped[str] = mapped_column(String(30))

    @classmethod
    def from_link(cls, definition: int, link: Link):
        print(definition, link.point_start)
        return cls(definition=definition,
                   start=link.point_start,
                   end=link.point_end,
                   depth=link.depth,
                   axis_start=link.axis_start,
                   axis_end=link.axis_end,
                   axis_value_start=link.axis_value_start,
                   axis_value_end=link.axis_value_end,
                   goal_start=link.goal_start,
                   goal_end=link.goal_end,
                   bucket_start=link.bucket_start,
                   bucket_end=link.bucket_end,
                   target=link.target_end-link.target_start,
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
    def from_link(cls, definition: int, link: Link):
        return cls(definition=definition,
                   start=link.axis_start,
                   value_start=link.axis_value_start,
                   value_end=link.axis_value_end,
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
    def from_link(cls, definition: int, link: Link):
        return cls(definition=definition,
                   start=link.goal_start,
                   target=link.item.target,
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
    hits:             Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_point_hit(cls, run: int, start: int, hits: int):
        return cls(run=run, start=start, hits=hits)

class BucketHitRow(BaseRow):
    __tablename__ = "bucket_hit"
    run:              Mapped[int] = mapped_column(Integer, primary_key=True)
    start:            Mapped[int] = mapped_column(Integer, primary_key=True)
    hits:             Mapped[int] = mapped_column(Integer)

    @classmethod
    def from_bucket_hit(cls, run: int, start: int, hits: int):
        return cls(run=run, start=start, hits=hits)

class Exporter:
    def __init__(self):
        self.engine = create_engine("sqlite://", echo=True)
        BaseRow.metadata.create_all(self.engine)

    def write_definition(self, root_point: CoverBase, chain: Link) -> int:
        with Session(self.engine) as session:
            # Insert a source row first
            def_row = DefinitionRow()
            session.add(def_row)
            session.commit()
            definition = def_row.definition

            for link in chain.iter():
                match link.item:
                    case Covergroup():
                        session.add(PointRow.from_link(definition, link))
                    case Coverpoint():
                        session.add(PointRow.from_link(definition, link))
                        # xyz
                        start = link.bucket_start
                        goal_start = link.goal_start
                        goal_offsets = {k:i for i,k in enumerate(link.item._goal_dict.keys())}
                        for offset, goal in enumerate(link.item.serialize_bucket_goals()):
                            session.add(BucketGoalRow.from_bucket_goal(definition, start + offset, goal_start + goal_offsets[goal]))
                    case Axis():
                        session.add(AxisRow.from_link(definition, link))
                        start = link.axis_value_start
                        for offset, axis_value in enumerate(link.item.values.keys()):
                            session.add(AxisValueRow.from_axis_value(definition, start + offset, axis_value))
                    case GoalItem():
                        session.add(GoalRow.from_link(definition, link))

            session.commit()
        
        return definition

    def write_run(self, root_point: CoverBase, definition: int, chain: Link) -> int:
            
        with Session(self.engine) as session:
            # Insert a source row first
            run_row = RunRow(definition=definition)
            session.add(run_row)
            session.commit()
            run = run_row.run

            # for link in chain.iter():
            #     match link.item:
            #         case Coverpoint():
            #             session.add(PointRow.from_link(definition, link))
            #             start = link.bucket_start
            #             for offset, hits in enumerate(link.item.serialize_bucket_hits()):
            #                 session.add(BucketHitRow.from_bucket_hit(definition, start + offset, hits))

            for start, hits in enumerate(root_point.serialize_point_hits()):
                session.add(PointHitRow.from_point_hit(run, start, hits))
            session.commit()

            for start, hits in enumerate(root_point.serialize_bucket_hits()):
                session.add(BucketHitRow.from_bucket_hit(run, start, hits))
            session.commit()

        return run

    def read_run(self, run: int):
        with Session(self.engine) as session:
            run_row = session.scalars(select(RunRow).where(RunRow.run==run)).one()
            definition = run_row.definition

            
            summary_table_columns = [
                Column("Name", justify="left", style="cyan", no_wrap=True),
                Column("Description", justify="left", style="cyan", no_wrap=True),
                Column("Hits", justify="right", style="cyan", no_wrap=True),
                Column("Target", justify="right", style="cyan", no_wrap=True),
                Column("Target %", justify="right", style="cyan", no_wrap=True),
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

            point_st = select(PointRow).where(PointRow.definition==definition).order_by(PointRow.start)
            point_hit_st = select(PointHitRow).where(PointHitRow.run==run).order_by(PointHitRow.start)

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


                summary_table.add_row(name, desc, str(hits), str(target), f"{target_percent:.2f}%")

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

                # [x.name for x in self.point_axes]


                # axes = session.scalars(axis_st).all()
                # axis_values = session.scalars(axis_value_st).all()

                # for axis_row in session.scalars(axis_st).all():
                #     start = axis_row.value_start
                #     end = axis_row.value_end
                #     breakpoint()



            console = Console()
            for point_table in point_tables:
                console.print(point_table)
            console.print(summary_table)




            

            # statement = select(PointRow).where(PointRow.definition==source)
            # for p in session.scalars(select(PointRow).where(PointRow.source==source)).all():
            #     # if p.end == p.start + 1:
            #     print(p.__dict__)
            #     breakpoint()
