from enum import Enum, auto

from dataclass_mapper import enum_mapper, enum_mapper_from, map_to


class Foo(Enum):
    x = auto()
    y = auto()


def test_enum_mapping():
    @enum_mapper(Foo, {"z": "y"})
    class FooSource(Enum):
        x = auto()
        z = auto()

    assert map_to(FooSource.x, Foo) == Foo.x
    assert map_to(FooSource.z, Foo) == Foo.y


def test_enum_mapping_from():
    @enum_mapper_from(Foo, {"y": "z"})
    class FooTarget(Enum):
        x = auto()
        z = auto()

    assert map_to(Foo.x, FooTarget) == FooTarget.x
    assert map_to(Foo.y, FooTarget) == FooTarget.z


class Bar(str, Enum):
    A = "AA"
    B = "BB"


def test_enum_mapping_between_str_and_int():
    @enum_mapper(Bar, {"C": "B"})
    class BarSource(Enum):
        A = 1
        C = -1

    assert map_to(BarSource.A, Bar) == Bar.A
    assert map_to(BarSource.C, Bar) == Bar.B
