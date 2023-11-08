from enum import auto, Enum
from typing import Any

class STORAGE_TYPE(Enum):
    sql = auto()
    file = auto()

class Master:
    id: int
    storage_type: STORAGE_TYPE
    # Each of these will point to where these are located
    # with meaning dependent on storage type
    point: str
    # The definition of axes
    axis: str
    # The values contained in each axis
    axis_value: str
    # The definition of goals e.g. ILLEGAL
    goal: str
    # The goal each bucket has
    bucket_goal: str
    # The hits each bucket has
    bucket_hit: str

class Coverpoint:
    id: int
    master: int

    hash: str 

    # These are the nested set bounds. Any descendents will have "start" and
    # "end" values between these. These would be indexed as a pair.
    start: int
    end: int

    # The depth in the tree, useful when finding parent / child relationships.
    depth: int

    # Coverpoint name
    name: str

    # Coverpoint description
    description: str

    # Where in the flat axis list the axes for this coverpoint can be located.
    axis_offset: int
    axis: int

    # Where in the flat axis value list the axis values for this coverpoint
    # can be located.
    axis_value_offset: int
    axis_value: int
    
    # Where in the flat goal list the goals for this coverpoint can be located.
    goal_offset: int
    goal: int

    # Where in the flat bucket-hit/bucket-goal lists the axes for this 
    # coverpoint can be located.
    bucket_offset: int
    bucket: int

class Axis:
    name: str
    description: int
    axis_value_offset: int
    axis_value: int

class AxisValue:
    value: Any

class Goal:
    name: str
    description: int
    target: int

class BucketGoal:
    goal: int

class BucketHit:
    hit: int




class Exporter:
    pass