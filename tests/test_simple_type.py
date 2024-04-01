from dataclasses import dataclass

from dataclass_mapper.mapper import create_mapper, map_to
from dataclass_mapper.mapper_mode import MapperMode


def test_extract_to_simple_type():
    @dataclass
    class Source:
        x: int

    create_mapper(Source, int, {"": "x"}, mapper_mode=MapperMode.CREATE)
    assert map_to(Source(5), int) == 5


def test_create_from_simple_type():
    @dataclass
    class Target:
        x: int

    create_mapper(int, Target, {"x": ""})
    assert map_to(42, Target) == Target(42)


def test_update_from_simple_type():
    @dataclass
    class Target:
        x: int

    create_mapper(int, Target, {"x": ""})

    target = Target(5)
    map_to(42, target)
    assert target == Target(42)


def test_simple_with_others():
    @dataclass
    class Target:
        x: int
        y: str

    create_mapper(int, Target, {"x": "", "y": lambda: "foo"})

    assert map_to(42, Target) == Target(x=42, y="foo")
