from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field

from safe_mapper.safe_mapper import map_to, safe_mapper


class BarPydantic(BaseModel):
    x: int = Field(default=5)
    y: str = "some_default"
    z: int = Field(default_factory=lambda: 1)


def test_pydantic_defaults():
    @safe_mapper(BarPydantic)
    class Bar(BaseModel):
        pass

    assert repr(map_to(Bar(), BarPydantic)) == repr(BarPydantic(x=5, y="some_default", z=1))


@dataclass
class BarDataclass:
    x: int = field(default=5)
    y: str = "some_default"
    z: int = field(default_factory=lambda: 1)


def test_dataclass_defaults():
    @safe_mapper(BarDataclass)
    @dataclass
    class Bar:
        pass

    assert map_to(Bar(), BarDataclass) == BarDataclass(x=5, y="some_default", z=1)


class FooPydantic(BaseModel):
    x: int = 42


def test_pydantic_optional_to_defaults():
    @safe_mapper(FooPydantic)
    class Foo(BaseModel):
        x: Optional[int]

    assert repr(map_to(Foo(x=5), FooPydantic)) == repr(FooPydantic(x=5))
    assert repr(map_to(Foo(x=None), FooPydantic)) == repr(FooPydantic(x=42))


@dataclass
class FooDataclass:
    x: int = 42


def test_dataclass_optional_to_defaults():
    @safe_mapper(FooDataclass)
    @dataclass
    class Foo:
        x: Optional[int]

    assert repr(map_to(Foo(x=5), FooDataclass)) == repr(FooDataclass(x=5))
    assert repr(map_to(Foo(x=None), FooDataclass)) == repr(FooDataclass(x=42))


class ATo(BaseModel):
    x: int


class BTo(BaseModel):
    aa: list[ATo] = Field(default_factory=list)


def test_pydantic_optional_to_defaults():
    @safe_mapper(ATo)
    class A(BaseModel):
        x: int

    @safe_mapper(BTo)
    class B(BaseModel):
        aa: Optional[list[A]]

    assert repr(map_to(B(aa=[A(x=42)]), BTo)) == repr(BTo(aa=[ATo(x=42)]))
    assert repr(map_to(B(aa=None), BTo)) == repr(BTo(aa=[]))
