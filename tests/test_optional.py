from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

from safe_mapper.safe_mapper import map_to, safe_mapper


class Bar(BaseModel):
    x: Optional[int]
    y: str


def test_simple_pydantic_mapper_with_optional_in_pydantic():
    @safe_mapper(Bar)
    class Foo(BaseModel):
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = Bar(x=42, y="answer")
    assert map_to(foo, Bar) == bar


@dataclass
class Baz:
    x: Optional[int]
    y: str


def test_simple_dataclass_mapper_with_optional_in_pydantic():
    @safe_mapper(Bar)
    @dataclass
    class Foo:
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = Bar(x=42, y="answer")
    assert map_to(foo, Bar) == bar
