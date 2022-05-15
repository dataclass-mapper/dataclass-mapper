from dataclasses import dataclass

from safe_mapper import DefaultFactory, map_to, safe_mapper, safe_mapper_from


@dataclass
class Bar:
    x: int


def test_default_values_in_mapping():
    @safe_mapper(Bar, {"x": DefaultFactory(lambda self: 42)})
    @dataclass
    class FooEmpty:
        pass

    assert map_to(FooEmpty(), Bar) == Bar(x=42)


@dataclass
class BarEmpty:
    pass


def test_default_values_in_mapping_from():
    @safe_mapper_from(BarEmpty, {"x": DefaultFactory(lambda self: 42)})
    @dataclass
    class Foo:
        x: int

    assert map_to(BarEmpty(), Foo) == Foo(x=42)
