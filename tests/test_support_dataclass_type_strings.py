from dataclasses import dataclass

from dataclass_mapper import map_to, mapper


@dataclass
class FooItem:
    ...


@dataclass
class Foo:
    x: "int"
    y: int
    item1: "FooItem"
    item2: FooItem


def test_support_dataclass_type_strings():
    @mapper(FooItem)
    @dataclass
    class BarItem:
        ...

    @mapper(Foo)
    @dataclass
    class Bar:
        x: int
        y: "int"
        item1: "BarItem"
        item2: BarItem

    bar = Bar(x=42, y=12345, item1=BarItem(), item2=BarItem())
    assert map_to(bar, Foo) == Foo(x=42, y=12345, item1=FooItem(), item2=FooItem())
