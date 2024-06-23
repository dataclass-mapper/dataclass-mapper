from dataclasses import dataclass
from typing import Generic, TypeVar

import pytest

from dataclass_mapper import create_mapper, map_to


def test_dataclass_used_unsupported_source_fieldtype_raises_typeerror():
    T = TypeVar("T")

    class SomeGeneric(Generic[T]):
        pass

    @dataclass
    class Source:
        value: SomeGeneric[int]  # unsupported type

    @dataclass
    class Target:
        value: int

    with pytest.raises(TypeError) as excinfo:
        create_mapper(Source, Target)

    assert str(excinfo.value) == f"Field type '{SomeGeneric[int]}' is not supported."


def test_dataclass_used_unsupported_target_fieldtype_raises_typeerror():
    T = TypeVar("T")

    class SomeGeneric(Generic[T]):
        pass

    @dataclass
    class Source:
        value: int

    @dataclass
    class Target:
        value: SomeGeneric[int]  # unsupported type

    with pytest.raises(TypeError) as excinfo:
        create_mapper(Source, Target)

    assert str(excinfo.value) == f"Field type '{SomeGeneric[int]}' is not supported."


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
