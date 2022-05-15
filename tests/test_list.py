from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from safe_mapper.safe_mapper import map_to, safe_mapper


class BarPydantic(BaseModel):
    x: int
    y: str


@dataclass
class BarDataclass:
    x: int
    y: str


class BazPydantic(BaseModel):
    bar: list[BarPydantic]


def test_rec_pydantic_mapper_with_optional():
    @safe_mapper(BarPydantic)
    class Bar(BaseModel):
        x: int
        y: str

    @safe_mapper(BazPydantic)
    class Baz(BaseModel):
        bar: list[Bar]

    baz_before = Baz(bar=[Bar(x=42, y="answer")])
    baz_after = BazPydantic(bar=[BarPydantic(x=42, y="answer")])
    assert repr(map_to(baz_before, BazPydantic)) == repr(baz_after)


class BazDataclass(BaseModel):
    bar: list[BarDataclass]


def test_rec_dataclass_mapper_with_optional():
    @safe_mapper(BarDataclass)
    @dataclass
    class Bar:
        x: int
        y: str

    @safe_mapper(BazDataclass)
    @dataclass
    class Baz:
        bar: list[Bar]

    baz_before = Baz(bar=[Bar(x=42, y="answer")])
    baz_after = BazDataclass(bar=[BarDataclass(x=42, y="answer")])
    assert map_to(baz_before, BazDataclass) == baz_after
