from dataclasses import dataclass
from typing import Generic, TypeVar

import pytest

from dataclass_mapper import create_mapper, map_to
from dataclass_mapper.mapper_mode import MapperMode


def test_dataclass_used_unsupported_fieldtype_raises_typeerror():
    T = TypeVar("T")

    class SomeGeneric(Generic[T]):
        pass

    @dataclass
    class ClassWithUnsupportedType:
        value: SomeGeneric[int]  # unsupported type

    @dataclass
    class ClassWithSupportedType:
        value: int

    with pytest.raises(TypeError) as excinfo:
        create_mapper(ClassWithUnsupportedType, ClassWithSupportedType)

    assert str(excinfo.value) == "Field type 'SomeGeneric' is not supported."

    with pytest.raises(TypeError) as excinfo:
        create_mapper(ClassWithSupportedType, ClassWithUnsupportedType)

    assert str(excinfo.value) == "Field type 'SomeGeneric' is not supported."


def test_dataclass_used_unsupported_fieldtype_updates_raises_typeerror():
    T = TypeVar("T")

    class SomeGeneric(Generic[T]):
        pass

    @dataclass
    class ClassWithUnsupportedType:
        value: SomeGeneric[int]  # unsupported type

    @dataclass
    class ClassWithSupportedType:
        value: int

    with pytest.raises(TypeError) as excinfo:
        create_mapper(ClassWithUnsupportedType, ClassWithSupportedType, mapper_mode=MapperMode.UPDATE)

    assert str(excinfo.value) == "Field type 'SomeGeneric' is not supported."

    with pytest.raises(TypeError) as excinfo:
        create_mapper(ClassWithSupportedType, ClassWithUnsupportedType, mapper_mode=MapperMode.UPDATE)

    assert str(excinfo.value) == "Field type 'SomeGeneric' is not supported."


def test_dataclass_unused_source_fields_are_ignored():
    T = TypeVar("T")

    class SomeGeneric(Generic[T]):
        pass

    @dataclass
    class Source:
        value: SomeGeneric[int]  # unsupported type

    @dataclass
    class Target:
        pass

    create_mapper(Source, Target)

    source = Source(SomeGeneric[int]())
    assert map_to(source, Target) == Target()


def test_dataclass_used_unsupported_fieldtype_can_still_copy():
    T = TypeVar("T")

    class SomeGeneric(Generic[T]):
        pass

    @dataclass
    class Source:
        value: SomeGeneric[int]  # unsupported type

    @dataclass
    class Target:
        value: SomeGeneric[int]  # unsupported type

    create_mapper(Source, Target)

    some_generic = SomeGeneric[int]()
    source = Source(some_generic)
    assert map_to(source, Target).value == some_generic
