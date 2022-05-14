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
