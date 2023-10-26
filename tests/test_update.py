from dataclasses import dataclass

from dataclass_mapper.mapper import map_to, mapper
from dataclass_mapper.mapping_method import init_with_default


@dataclass
class Foo:
    x: int
    y: str


def test_simple_update():
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
    @mapper(Foo, {"x": init_with_default()})
    @dataclass
    class FooUpdate:
        y: str

    foo = Foo(x=42, y="Something")
    foo_update = FooUpdate(y="Else")

    map_to(foo_update, foo)

    assert foo == Foo(x=42, y="Else")
