from dataclasses import dataclass

from dataclass_mapper import create_mapper, map_to


def test_create():
    @dataclass
    class TargetItem:
        x: int

    @dataclass
    class Target:
        item: "TargetItem"

    @dataclass
    class SourceItem:
        x: int

    @dataclass
    class Source:
        item: "SourceItem"

    create_mapper(SourceItem, TargetItem)
    create_mapper(Source, Target)
    assert map_to(Source(item=SourceItem(x=42)), Target) == Target(item=TargetItem(x=42))
