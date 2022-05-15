from dataclasses import dataclass

from safe_mapper import map_to, safe_mapper, safe_mapper_from


@dataclass
class Bar:
    x: int
    y: str


def test_default_values_in_mapping():
    @safe_mapper(Bar, {"x": lambda: 42, "y": lambda self: self.name})
    @dataclass
    class FooEmpty:
        name: str

    assert map_to(FooEmpty(name="Sally"), Bar) == Bar(x=42, y="Sally")


@dataclass
class BarEmpty:
    pass


@safe_mapper_from(BarEmpty, {"x": lambda: 42})
@dataclass
class Foo:
    x: int


def test_default_values_in_mapping_from():
    assert map_to(BarEmpty(), Foo) == Foo(x=42)
