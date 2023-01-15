from dataclasses import dataclass

from pydantic import BaseModel

from dataclass_mapper import map_to, mapper


def test_support_dataclass_type_strings():
    @dataclass
    class FooItem:
        ...

    @dataclass
    class Foo:
        x: "int"
        y: int
        item1: "FooItem"
        item2: FooItem

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


def test_support_pydantic_type_strings():
    class FooItem(BaseModel):
        ...

    class Foo(BaseModel):
        x: "int"
        y: int
        item1: "FooItem"
        item2: FooItem

    @mapper(FooItem)
    class BarItem(BaseModel):
        ...

    @mapper(Foo)
    class Bar(BaseModel):
        x: int
        y: "int"
        item1: "BarItem"
        item2: BarItem

    bar = Bar(x=42, y=12345, item1=BarItem(), item2=BarItem())
    expected_foo = Foo(x=42, y=12345, item1=FooItem(), item2=FooItem())
    assert str(map_to(bar, Foo)) == str(expected_foo)
