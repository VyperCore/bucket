from dataclasses import asdict, dataclass, replace
import itertools
from typing import Iterable, Iterator, Self

from .goal import GoalItem

from .axis import Axis

@dataclass(kw_only=True)
class PointStartPos:
    depth: int = 0
    start: int = 0
    axis_start: int = 0
    axis_value_start: int = 0
    goal_start: int = 0
    bucket_start: int = 0
    target_start: int = 0

    def to_child_start(self):
        return replace(self, start=self.start+1, depth=self.depth+1)
    
    def to_pos_from_last(self, last: "PointPos|None"):
        if last is None:
            return PointPos(
                **asdict(self),
                end=self.start
            )
        return PointPos(
            **asdict(self),
            end=last.end,
            axis_end=last.axis_end,
            axis_value_end=last.axis_value_end,
            goal_end=last.goal_end,
            bucket_end=last.bucket_end,
            target_end=last.target_end,
        )

@dataclass(kw_only=True)
class PointPos(PointStartPos):
    end: int = 0
    axis_end: int = 0
    axis_value_end: int = 0
    goal_end: int = 0
    bucket_end: int = 0
    target_end: int = 0

    def next_sibling(self):
        return PointStartPos(
            depth=self.depth, 
            start=self.end, 
            axis_start=self.axis_end,
            axis_value_start=self.axis_value_end,
            goal_start=self.goal_end,
            bucket_start=self.bucket_end,
            target_start=self.target_end,
        )
    

class CoverBase:
    pos: None | PointPos
    name: str
    description: str
    target: int
    hits: int

    def setup(self):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def sample(self, trace):
        raise NotImplementedError("This needs to be implemented by the coverpoint")

    def identify(self, start: PointStartPos | None = None) -> PointPos: ...
    def serialize_points(self) -> Iterator[Self]: ...
    def serialize_axes(self) -> Iterator[Axis]: ...
    def serialize_axis_values(self) -> Iterator[str]: ...
    def serialize_goals(self) -> Iterator[GoalItem]: ...
    def serialize_bucket_goals(self) -> Iterator[int]: ...
    def serialize_bucket_targets(self) -> Iterator[int]: ...
    def serialize_bucket_hits(self) -> Iterator[int]: ...
    def serialize_point_hits(self) -> Iterator[int]: ...

    def export(self):
        self.identify()
        from .export.sql import Exporter

        exporter = Exporter()
        definition = exporter.write_definition(self)

        run = exporter.write_run(self, definition)
        exporter.read_run(run)

        # import sqlalchemy
        # from sqlalchemy import orm, Integer, String, select

        # class Base(orm.DeclarativeBase): ...

        # class Point(Base):
        #     __tablename__ = "point"
        #     id:               orm.Mapped[int] = orm.mapped_column(primary_key=True, autoincrement=True)
        #     depth:            orm.Mapped[int] = orm.mapped_column(Integer)
        #     left:             orm.Mapped[int] = orm.mapped_column(Integer)
        #     right:            orm.Mapped[int] = orm.mapped_column(Integer)
        #     axis_start:       orm.Mapped[int] = orm.mapped_column(Integer)
        #     axis_size:        orm.Mapped[int] = orm.mapped_column(Integer)
        #     axis_value_start: orm.Mapped[int] = orm.mapped_column(Integer)
        #     axis_value_size:  orm.Mapped[int] = orm.mapped_column(Integer)
        #     goal_start:       orm.Mapped[int] = orm.mapped_column(Integer)
        #     goal_size:        orm.Mapped[int] = orm.mapped_column(Integer)
        #     bucket_start:     orm.Mapped[int] = orm.mapped_column(Integer)
        #     bucket_size:      orm.Mapped[int] = orm.mapped_column(Integer)
        #     name:             orm.Mapped[str] = orm.mapped_column(String(30))
        #     description:      orm.Mapped[str] = orm.mapped_column(String(30))

        #     @classmethod
        #     def create(cls, point: CoverBase):
        #         return Point(**{k:v for k,v in zip(point.field_keys(), point.field_values())})


        # engine = sqlalchemy.create_engine("sqlite://", echo=True)

        # Base.metadata.create_all(engine)

        # with orm.Session(engine) as session:
        #     for item in self.serialize_points():
        #         session.add(Point.create(item))
        #     session.commit()

        # stmt = select(Point).where(Point.left.in_([0, 1, 2, 3]))
        # for p in session.scalars(stmt):
        #     print(p)

        # with open('./points.csv', mode='w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(self.field_keys())
        #     for item in self.serialize_points():
        #         writer.writerow(item.field_values())

        # with open('./axes.csv', mode='w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(Axis.field_keys())
        #     for item in self.serialize_axes():
        #         writer.writerow(item.field_values())

        # with open('./goals.csv', mode='w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(GoalItem.field_keys())
        #     for item in self.serialize_goals():
        #         writer.writerow(item.field_values())

        # with open('./axis_values.csv', mode='w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(('Axis Value',))
        #     for item in self.serialize_axis_values():
        #         writer.writerow((item,))

        # with open('./bucket_goals.csv', mode='w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(('Bucket Goal',))
        #     for item in self.serialize_bucket_goals():
        #         writer.writerow((item,))

        # with open('./bucket_hits.csv', mode='w') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(('Bucket Hits',))
        #     for item in self.serialize_bucket_hits():
        #         writer.writerow((item,))

        # for cp in self.iter_tree():
        #     print(cp.name, cp._offset_sizes)
        #     breakpoint()

        
        # print(self.offset, self.size, self.name)
        # for cp in self.coverpoints.values():
        #     # print(f'Exporting coverage for "{cp.name}"')
        #     cp.export_coverage()

        # for cg in self.covergroups.values():
        #     cg.export_coverage()

    @classmethod
    def field_keys(cls):
        return ("depth", "start", "end", "axis_start", "axis_end", "axis_value_start", "axis_value_end", "goal_start", "goal_end", "bucket_start", "bucket_end", "target", "name", "description")

    def field_values(self):
        if (p:=self.pos) is None:
            raise RuntimeError("Identify must be called before coverpoint values exist")
        return (p.depth, p.start, p.end, p.axis_start, p.axis_end, p.axis_value_start, p.axis_value_end, p.goal_start, p.goal_end, p.bucket_start, p.bucket_end, p.target_end - p.target_start, self.name, self.description)

class Covergroup(CoverBase):
    """This class groups coverpoints together, and adds them to the hierarchy"""

    def __init__(self, name, description):
        """
        Parameters:
            name: Name of covergroup
            description: Description of covergroup
            cvg_tier: what coverage tier is being run [0..3]
        """

        self.name = name
        self.description = description

        self.coverpoints = {}
        self.covergroups = {}
        self.setup()

        self.pos = None

    def add_coverpoint(self, coverpoint):
        """
        Add a coverpoint instance to the covergroup
        Parameters:
            coverpoint: instance of a coverpoint
            trigger:    [optional] specific trigger on which to sample the coverpoint
        """
        if coverpoint.name in self.coverpoints:
            raise Exception("Coverpoint names must be unique within a covergroup")

        self.coverpoints[coverpoint.name] = coverpoint
        setattr(self, coverpoint.name, coverpoint)

    def add_covergroup(self, covergroup):
        """
        Add a covergroup instance to the covergroup
        Parameters:
            covergroup: instance of a covergroup
        """
        if covergroup.name in self.covergroups:
            raise Exception("Covergroup names must be unique within a covergroup")

        self.covergroups[covergroup.name] = covergroup
        setattr(self, covergroup.name, covergroup)

    def print_tree(self, indent=0):
        """Print out coverage hierarch from this covergroup down"""
        if indent == 0:
            print("COVERAGE_TREE")
            print(f"* {self.name}: {self.description}")
        indent += 1
        indentation = "    " * indent
        for cp in self.coverpoints.values():
            print(f"{indentation}|-- {cp.name}: {cp.description}")

        for cg in self.covergroups.values():
            print(f"{indentation}|-- {cg.name}: {cg.description}")
            cg.print_tree(indent + 1)

    def sample(self, trace):
        """Call sample on all sub-groups and coverpoints, passing in trace"""
        for cp in self.coverpoints.values():
            cp.sample(trace)

        for cg in self.covergroups.values():
            cg.sample(trace)

    def iter_children(self) -> Iterable[CoverBase]:
        yield from itertools.chain(self.coverpoints.values(), self.covergroups.values())

    def identify(self, start: PointStartPos | None = None) -> PointPos:
        start = start or PointStartPos()
        child_start = start.to_child_start()
        child_pos = None
        for child in self.iter_children():
            child_pos = child.identify(child_start)
            child_start = child_pos.next_sibling()
        self.pos = start.to_pos_from_last(child_pos)
        return self.pos
    
    def serialize_point_hits(self):
        total_hits = 0
        descendant_hits = []
        for child in self.iter_children():
            child_hits, *grandchild_hits = list(child.serialize_point_hits())
            total_hits += child_hits
            descendant_hits.append(child_hits)
            descendant_hits += grandchild_hits
        yield total_hits
        yield from descendant_hits

    def serialize_points(self):
        yield self
        for child in self.iter_children():
            yield from child.serialize_points()

    def serialize_axes(self):
        for child in self.iter_children():
            yield from child.serialize_axes()

    def serialize_axis_values(self):
        for child in self.iter_children():
            yield from child.serialize_axis_values()

    def serialize_goals(self):
        for child in self.iter_children():
            yield from child.serialize_goals()

    def serialize_bucket_goals(self):
        for child in self.iter_children():
            yield from child.serialize_bucket_goals()

    def serialize_bucket_targets(self):
        for child in self.iter_children():
            yield from child.serialize_bucket_targets()

    def serialize_bucket_hits(self):
        for child in self.iter_children():
            yield from child.serialize_bucket_hits()
