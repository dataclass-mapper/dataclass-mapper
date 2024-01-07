from dataclasses import dataclass
from enum import Enum

import pytest

from dataclass_mapper import create_mapper, enum_mapper, map_to, mapper


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


def test_mapper_fails_for_enums():
    class EnumTarget(str, Enum):
        A = "A"

    with pytest.raises(ValueError) as excinfo:

        @mapper(EnumTarget)
        class EnumSource(str, Enum):
            A = "A"

    assert str(excinfo.value) == "`mapper` does not support enum classes, use `enum_mapper` instead"


def test_enum_mapper_failes_for_normal_classes():
    @dataclass
    class Target:
        pass

    with pytest.raises(ValueError) as excinfo:

        @enum_mapper(Target)
        @dataclass
        class Source:
            pass

    assert str(excinfo.value) == "`enum_mapper` does only support enum classes, use `mapper` for other classes"


def test_class_not_mappable():
    class Foo:
        pass

    with pytest.raises(NotImplementedError) as excinfo:
        create_mapper(Foo, Foo)

    assert str(excinfo.value) == "only dataclasses, pydantic and sqlalchemy classes are supported"
