from dataclasses import dataclass
from typing import List, Optional

import pytest

from dataclass_mapper.mapper import create_mapper, map_to, mapper
from dataclass_mapper.mapper_mode import MapperMode
from dataclass_mapper.mapping_method import ignore, update_only_if_set


def test_simple_update():
    @dataclass
    class Foo:
        x: int
        y: str

    @mapper(Foo)
    @dataclass
    class FooUpdate:
        x: int
        y: str

    foo = Foo(x=42, y="Something")
    foo_update = FooUpdate(x=5, y="Else")

    map_to(foo_update, foo)

    assert foo == Foo(x=5, y="Else")


def test_partial_update():
    @dataclass
    class Foo:
        x: int
        y: str

    @mapper(Foo, {"x": ignore()}, mapper_mode=MapperMode.UPDATE)
    @dataclass
    class FooUpdate:
        y: str

    foo = Foo(x=42, y="Something")
    foo_update = FooUpdate(y="Else")

    map_to(foo_update, foo)

    assert foo == Foo(x=42, y="Else")


def test_self_update():
    @dataclass
    class Foo:
        x: int

    create_mapper(Foo, Foo)

    foo = Foo(x=42)
    foo_update = Foo(x=5)

    map_to(foo_update, foo)
    assert foo == Foo(x=5)


def test_recursive_update_using_overwrite():
    @dataclass
    class Foo:
        x: int
        y: str

    @dataclass
    class Bar:
        foo: Foo
        x: int

    @mapper(Foo, {"y": ignore()}, mapper_mode=MapperMode.UPDATE)
    @dataclass
    class FooUpdate:
        x: int

    @mapper(Bar, {"x": ignore()}, mapper_mode=MapperMode.UPDATE)
    @dataclass
    class BarUpdate:
        foo: FooUpdate

    bar = Bar(foo=Foo(x=42, y="Something"), x=1)
    bar_update = BarUpdate(foo=FooUpdate(x=5))

    map_to(bar_update, bar)

    assert bar == Bar(foo=Foo(x=5, y="Something"), x=1)


def test_recursive_update_with_missing_recursive_creator_fails():
    @dataclass
    class Foo:
        x: int
        y: str

    @dataclass
    class Bar:
        foo: List[Foo]
        x: int

    @mapper(Foo, {"y": ignore()}, mapper_mode=MapperMode.UPDATE)
    @dataclass
    class FooUpdate:
        x: int

    with pytest.raises(TypeError) as excinfo:

        @mapper(Bar, {"x": ignore()}, mapper_mode=MapperMode.UPDATE)
        @dataclass
        class BarCreator:
            foo: List[FooUpdate]

    assert (
        "'foo' of type 'List[FooUpdate]' of 'BarCreator' cannot be converted to 'foo' of type 'List[Foo]' of 'Bar'. "
        "The mapping is missing, or only exists for the MapperMode.UPDATE mode." == str(excinfo.value)
    )


def test_update_only_if_set():
    @dataclass
    class Foo:
        x: int

    @dataclass
    class FooUpdate:
        x: Optional[int]

    with pytest.raises(ValueError) as excinfo:
        create_mapper(FooUpdate, Foo, {"x": update_only_if_set()})
    assert (
        str(excinfo.value)
        == "'x' of 'Foo' cannot be set to update_only_if_set() if the mapper mode is not set to MapperMode.UPDATE."
    )

    create_mapper(FooUpdate, Foo, {"x": update_only_if_set()}, mapper_mode=MapperMode.UPDATE)

    foo = Foo(x=42)
    map_to(FooUpdate(x=None), foo)
    assert foo.x == 42
    map_to(FooUpdate(x=5), foo)
    assert foo.x == 5
