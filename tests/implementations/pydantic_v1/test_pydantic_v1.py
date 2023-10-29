from typing import Dict, List, Optional

import pytest

from dataclass_mapper.implementations.pydantic_v1 import pydantic_version
from dataclass_mapper.mapper import map_to, mapper

if pydantic_version()[0] != 1:
    pytest.skip("V1 validators syntax", allow_module_level=True)

from pydantic import BaseModel, Field, validator


class Bar(BaseModel):
    x: int
    y: str


def test_simple_pydantic_mapper():
    @mapper(Bar)
    class Foo(BaseModel):
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = Bar(x=42, y="answer")
    assert map_to(foo, Bar) == bar


class Baz(BaseModel):
    bar: Bar


def test_recursive_pydantic_mapper():
    @mapper(Bar)
    class Bar2(BaseModel):
        x: int
        y: str

    @mapper(Baz)
    class Baz2(BaseModel):
        bar: Bar2

    data: Dict = {"bar": {"x": 42, "y": "answer"}}
    assert repr(map_to(Baz2(**data), Baz)) == repr(Baz(**data))


class X(BaseModel):
    x1: Optional[int] = None
    x2: Optional[int] = None


class UnsetFields(BaseModel):
    a: int
    b1: Optional[int] = Field()
    b2: Optional[int] = Field()
    b3: Optional[int] = Field()
    c1: Optional[int] = Field(None)
    c2: Optional[int] = Field(None)
    c3: Optional[int] = Field(None)
    d1: Optional[int] = None
    d2: Optional[int] = None
    d3: Optional[int] = None
    x1: Optional[X] = None
    x2: Optional[X] = None
    x3: Optional[X] = None
    l1: Optional[List[X]] = None
    l2: Optional[List[X]] = None
    l3: Optional[List[X]] = None


def test_maintain_unset_field_infos():
    @mapper(X)
    class Y(BaseModel):
        x1: Optional[int] = None
        x2: Optional[int] = None

    @mapper(UnsetFields)
    class UnsetFieldsSource(BaseModel):
        a: int
        b1: Optional[int] = Field()
        b2: Optional[int] = Field()
        b3: Optional[int] = Field()
        c1: Optional[int] = Field(None)
        c2: Optional[int] = Field(None)
        c3: Optional[int] = Field(None)
        d1: Optional[int] = None
        d2: Optional[int] = None
        d3: Optional[int] = None
        x1: Optional[Y] = None
        x2: Optional[Y] = None
        x3: Optional[Y] = None
        l1: Optional[List[Y]] = None
        l2: Optional[List[Y]] = None
        l3: Optional[List[Y]] = None

    source = UnsetFieldsSource(
        a=1, b1=1, b2=None, c1=1, c2=None, d1=1, d2=None, x1=Y(x1=1), x2=None, l1=[Y(x1=1)], l2=None
    )  # type: ignore[call-arg] # for pydantic v2
    assert source.__fields_set__ == {
        "a",
        "b1",
        "b2",
        "c1",
        "c2",
        "d1",
        "d2",
        "x1",
        "x2",
        "l1",
        "l2",
    }
    assert source.x1 and source.x1.__fields_set__ == {"x1"}
    assert source.l1 and source.l1[0].__fields_set__ == {"x1"}
    mapped = map_to(source, UnsetFields)
    assert mapped.__fields_set__ == {
        "a",
        "b1",
        "b2",
        "c1",
        "c2",
        "d1",
        "d2",
        "x1",
        "x2",
        "l1",
        "l2",
    }
    assert mapped.x1 and mapped.x1.__fields_set__ == {"x1"}
    assert mapped.l1 and mapped.l1[0].__fields_set__ == {"x1"}


def test_pydantic_with_alias():
    class BarWithAlias(BaseModel):
        x: int = Field(alias="xxx")
        y: str

        @validator("x")
        def val_x(cls, v):
            return v

        class Config:
            fields = {"y": "yyy"}

    @mapper(BarWithAlias)
    class Foo(BaseModel):
        x: int
        y: str

    foo = Foo(x=42, y="answer")
    bar = BarWithAlias(xxx=42, yyy="answer")  # type: ignore[call-arg]
    assert map_to(foo, BarWithAlias) == bar


def test_pydantic_with_alias_allow_population_with_fields():
    class BarWithAliasAllowFieldPopulation(BaseModel):
        x: int = Field(alias="x x")

        @validator("x")
        def val_x(cls, v):
            return v

        class Config:
            allow_population_by_field_name = True

    @mapper(BarWithAliasAllowFieldPopulation)
    class Foo(BaseModel):
        x: int

    foo = Foo(x=42)
    bar = BarWithAliasAllowFieldPopulation(x=42)  # type: ignore[call-arg] # for pydantic v2
    assert map_to(foo, BarWithAliasAllowFieldPopulation) == bar
