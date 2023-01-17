from dataclasses import dataclass
from enum import Enum

import pytest

from dataclass_mapper import enum_mapper, map_to, mapper


@dataclass
class Foo:
    pass


@dataclass
class Bar:
    pass


def test_not_mappable_without_mapper_definition():
    with pytest.raises(NotImplementedError) as excinfo:
        map_to(Foo(), Bar)

    assert str(excinfo.value) == "Object of type 'Foo' cannot be mapped to 'Bar'"


def test_mapping_already_exists():
    with pytest.raises(AttributeError) as excinfo:

        @mapper(Foo)
        @mapper(Foo)
        @dataclass
        class FooSource:
            pass

    assert str(excinfo.value) == "There already exists a mapping between 'FooSource' and 'Foo'"


def test_enum_mapping_already_exists():
    class EnumTarget(str, Enum):
        A = "A"

    with pytest.raises(AttributeError) as excinfo:

        @enum_mapper(EnumTarget)
        @enum_mapper(EnumTarget)
        class EnumSource(str, Enum):
            A = "A"

    assert str(excinfo.value) == "There already exists a mapping between 'EnumSource' and 'EnumTarget'"
