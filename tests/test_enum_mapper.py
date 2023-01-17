import sys
from enum import Enum, auto

import pytest

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


def test_enum_mapping_with_actual_members():
    @enum_mapper(Bar, {"C": Bar.B})
    class BarSource(Enum):
        A = 1
        C = -1

    assert map_to(BarSource.A, Bar) == Bar.A
    assert map_to(BarSource.C, Bar) == Bar.B


def test_enum_mapper_wrong_source():
    with pytest.raises(ValueError) as excinfo:

        @enum_mapper(Bar, {"CC": "B"})
        class BarSource(Enum):
            A = 1
            C = -1

    assert "The mapping key 'CC' must be a member of the source enum 'BarSource' or a string with its name" in str(
        excinfo.value
    )


def test_enum_mapper_wrong_target():
    with pytest.raises(ValueError) as excinfo:

        @enum_mapper(Bar, {"C": "BB"})
        class BarSource(Enum):
            A = 1
            C = -1

    assert "The mapping key 'BB' must be a member of the target enum 'Bar' or a string with its name" in str(
        excinfo.value
    )


def test_enum_mapper_missing_mapping():
    with pytest.raises(ValueError) as excinfo:

        @enum_mapper(Bar)
        class BarSource(Enum):
            A = 1
            C = -1

    assert ("The member 'C' of the source enum 'BarSource' doesn't have a mapping.") in str(excinfo.value)


@pytest.mark.skipif(sys.version_info < (3, 11), reason="StrEnum was introduced in 3.11")
def test_StrEnum():
    from enum import IntEnum, StrEnum

    class StrTarget(StrEnum):
        ABC = "ABC"
        DEF = "DEF"

    @enum_mapper(StrTarget)
    class StrSource(IntEnum):
        ABC = auto()
        DEF = auto()

    assert map_to(StrSource.ABC, StrTarget) == StrTarget.ABC
    assert map_to(StrSource.DEF, StrTarget) == StrTarget.DEF
