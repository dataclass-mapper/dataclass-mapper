from typing import Optional

from pydantic import BaseModel, Field

from dataclass_mapper.mapper import map_to, mapper


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

    data: dict = {"bar": {"x": 42, "y": "answer"}}
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
    l1: Optional[list[X]] = None
    l2: Optional[list[X]] = None
    l3: Optional[list[X]] = None


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
        l1: Optional[list[Y]] = None
        l2: Optional[list[Y]] = None
        l3: Optional[list[Y]] = None

    source = UnsetFieldsSource(
        a=1, b1=1, b2=None, c1=1, c2=None, d1=1, d2=None, x1=Y(x1=1), x2=None, l1=[Y(x1=1)], l2=None
    )
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
    assert source.x1.__fields_set__ == {"x1"}
    assert source.l1[0].__fields_set__ == {"x1"}
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
    assert mapped.x1.__fields_set__ == {"x1"}
    assert mapped.l1[0].__fields_set__ == {"x1"}
