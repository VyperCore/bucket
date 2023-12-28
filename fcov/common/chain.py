from collections import defaultdict
from typing import Any, Hashable, Optional, Generic, Protocol, Self, TypeVar

class Index:
    def __init__(self):
        self.values = defaultdict(list)

    def add(self, typ: Hashable, item: "Link"):
        self.values[typ].append(item)
    
    def iter(self, typ: Hashable):
        yield from self.values[typ]

class Addable(Protocol):
    def __add__(self, other: Self) -> Self: ...


_LinkType = TypeVar("_LinkType", bound=Addable)
class OpenLink(Generic[_LinkType]):
    def __init__(self,
                 start: _LinkType,
                 index: Optional[Index]=None,
                 depth: int=0):
        self.start = start
        self.index = index or Index()
        self.depth = depth

    def link_down(self):
        return OpenLink[_LinkType](
            start=self.start,
            index=self.index,
            depth=self.depth+1)
    
    def close(self, item: Any, *, typ: Hashable, link: Optional[_LinkType]=None, child: Optional["Link[_LinkType]"]=None):
        if child is None:
            end = self.start 
        else:
            end = child.end

        if link is not None:
            end += link

        return Link[_LinkType](
            self,
            item=item,
            typ=typ,
            end=end
        )
    
class Link(Generic[_LinkType]):
    def __init__(self, open_link: OpenLink[_LinkType], item: Any, typ: Hashable, end: _LinkType):
        self.start = open_link.start
        self.depth = open_link.depth
        self.index = open_link.index
        self.item = item
        self.end = end
        self.index.add(typ, self)
    
    def link_across(self):
        return OpenLink[_LinkType](
            start=self.end,
            index=self.index, 
            depth=self.depth)
