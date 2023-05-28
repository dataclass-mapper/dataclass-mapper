from dataclasses import dataclass

import pytest

from dataclass_mapper import map_to, mapper, mapper_from


def test_default_values_in_mapping():
    @dataclass
    class Bar:
        x: int
        y: str

    @mapper(Bar, {"x": lambda: 42, "y": lambda self: self.name})
    @dataclass
    class FooEmpty:
        name: str

    assert map_to(FooEmpty(name="Sally"), Bar) == Bar(x=42, y="Sally")


def test_default_values_in_mapping_from():
    @dataclass
    class BarEmpty:
        pass

    @mapper_from(BarEmpty, {"x": lambda: 42})
    @dataclass
    class Foo:
        x: int

    assert map_to(BarEmpty(), Foo) == Foo(x=42)


def test_callable_factory():
    @dataclass
    class Target:
        x: int

    class Incrementor:
        def __init__(self):
            self.value: int = 0

        def __call__(self) -> int:
            self.value += 1
            return self.value

    @mapper(Target, {"x": Incrementor()})
    @dataclass
    class Source:
        pass

    assert map_to(Source(), Target) == Target(x=1)
    assert map_to(Source(), Target) == Target(x=2)


def test_refuse_factory_with_multiple_parameters():
    @dataclass
    class Target:
        x: int

    with pytest.raises(ValueError) as excinfo:

        @mapper(Target, {"x": lambda a, b: a + b})
        @dataclass
        class Source:
            pass

    assert str(excinfo.value) == "'x' of 'Target' cannot be mapped using a factory with more than one parameter"
