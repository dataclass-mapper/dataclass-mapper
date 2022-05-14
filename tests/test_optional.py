from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from safe_mapper.safe_mapper import map_to, safe_mapper


class BarPydantic(BaseModel):
    x: Optional[int]
    y: str


def test_simple_pydantic_mapper_with_optional():
    @safe_mapper(BarPydantic)
    class Foo(BaseModel):
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = BarPydantic(x=42, y="answer")
    assert map_to(foo, BarPydantic) == bar


@dataclass
class BarDataclass:
    x: Optional[int]
    y: str


def test_simple_dataclass_mapper_with_optional():
    @safe_mapper(BarDataclass)
    @dataclass
    class Foo:
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = BarDataclass(x=42, y="answer")
    assert map_to(foo, BarDataclass) == bar


class BazPydantic(BaseModel):
    bar: Optional[BarPydantic]


def test_rec_pydantic_mapper_with_optional():
    @safe_mapper(BarPydantic)
    class Bar(BaseModel):
        x: int
        y: str

    @safe_mapper(BazPydantic)
    class Baz(BaseModel):
        bar: Bar

    baz_before = Baz(bar=Bar(x=42, y="answer"))
    baz_after = BazPydantic(bar=BarPydantic(x=42, y="answer"))
    assert repr(map_to(baz_before, BazPydantic)) == repr(baz_after)


# class BazPydantic(BaseModel):
#     bar: Optional[BarPydantic]


# def test_rec_pydantic_mapper_with_optional():
#     @safe_mapper(BarPydantic)
#     class Bar(BaseModel):
#         x: int
#         y: str

#     @safe_mapper(BazPydantic)
#     class Baz(BaseModel):
#         bar: Bar

#     baz_before = Baz(bar=Bar(x=42, y="answer"))
#     baz_after = BazPydantic(bar=BarPydantic(x=42, y="answer"))
#     assert repr(map_to(baz_before, BazPydantic)) == repr(baz_after)
