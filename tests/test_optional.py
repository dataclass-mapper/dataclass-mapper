from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from dataclass_mapper.mapper import map_to, mapper


class BarPydantic(BaseModel):
    x: Optional[int]
    y: str


def test_simple_pydantic_mapper_with_optional():
    @mapper(BarPydantic)
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
    @mapper(BarDataclass)
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
    @mapper(BarPydantic)
    class Bar(BaseModel):
        x: int
        y: str

    @mapper(BazPydantic)
    class Baz(BaseModel):
        bar: Optional[Bar]

    baz_before = Baz(bar=Bar(x=42, y="answer"))
    baz_after = BazPydantic(bar=BarPydantic(x=42, y="answer"))
    assert repr(map_to(baz_before, BazPydantic)) == repr(baz_after)

    baz_before2 = Baz(bar=None)
    baz_after2 = BazPydantic(bar=None)
    assert repr(map_to(baz_before2, BazPydantic)) == repr(baz_after2)


@dataclass
class BazDataclass:
    bar: Optional[BarDataclass]


def test_rec_dataclass_mapper_with_optional():
    @mapper(BarDataclass)
    @dataclass
    class Bar:
        x: int
        y: str

    @mapper(BazDataclass)
    @dataclass
    class Baz:
        bar: Optional[Bar]

    baz_before = Baz(bar=Bar(x=42, y="answer"))
    baz_after = BazDataclass(bar=BarDataclass(x=42, y="answer"))
    assert map_to(baz_before, BazDataclass) == baz_after

    baz_before2 = Baz(bar=None)
    baz_after2 = BazDataclass(bar=None)
    assert map_to(baz_before2, BazDataclass) == baz_after2
